from typing import List, Iterator, Dict, Optional, Any, Type
import logging
# import socket
import sys
import multiprocessing
import queue
from time import time
import asyncio
import functools
import os
# import uuid

import json

from coinpy.core import JsonDict
from coinpy.core.block import Block, GENESIS_BLOCK
from coinpy.core.output import Output, OutputID
from coinpy.core.transaction import Transaction, TransactionID, Utils
from coinpy.core.crypto import Pubaddr, PrivkeyStorage, ID
from coinpy.core.errors import TransactionRulesError

from .consensus import Rules, BlockRulesError, TransactionRulesError
from .miner import Miner, ExternalMiner, block_mine_internal
from .peer import Peer, PeerAddr, Message

from .commands import AnnounceBlockCommand, InfoCommand, GreetCommand

logger = logging.getLogger(__name__)

class Node(Peer):
    def __init__(self, loop: asyncio.AbstractEventLoop, **config: Any) -> None:
        self.config = config
        Rules.block_valid_difficulty(GENESIS_BLOCK)
        self.__ledger: List[Block] = [GENESIS_BLOCK]
        self.__unprocess_trxs: Dict[TransactionID, Transaction] = {}
        self.__unspent_outs: Dict[OutputID, Output] = {}
        self.__io_loop = loop
        super().__init__(self.__io_loop, self.config.get('addr', PeerAddr(('127.0.0.1', 5001))))
        if 'neighbors' in self.config:
            self.neighbors_add(self.config['neighbors'])

    async def start(self) -> None:
        logger.info(f'starting node with {self.config}')
        await  super().start()
        self.commnads_register(
                [(self, AnnounceBlockCommand),
                 (self, GreetCommand),
                 (self, InfoCommand)])

    async def stop(self) -> None:
        logger.info('stopping node')
        await super().stop()

    def block_add_to_blockchain(self, blk_new: Block) -> None:
        logger.debug(f'adding block {blk_new.id}')
        try:
            self.block_validate(blk_new)
            self.__block_proccess(blk_new)
            self.__ledger.append(blk_new)
        except Exception as e:
            logger.debug(f'consensus error {str(e)}')

    def block_validate(self, blk: Block) -> None:
        logger.debug(f'validating block {blk.id}')
        self.__block_assebmle_helper_data(blk)
        # consensus
        Rules.block_valid(self.__ledger[-1], blk)
        # valid blocks transactions and inputs
        for trx in blk.transactions:
            if Utils.transaction_is_coinbase(trx):
                return
            for inp_id in trx.inputs:
                if inp_id not in self.__unspent_outs:
                    raise TransactionRulesError('spent output as input')

    def __block_proccess(self, blk: Block) -> None:
        logger.debug(f'proccessing block {blk.id}')
        for trx in blk.transactions:
            for unspout in trx.outputs: # type: ignore
                # add trx outputs into unspent outputs
                self.__unspent_outs[unspout.id] = unspout
            if not Utils.transaction_is_coinbase(trx):
                for inp_id in trx.inputs: # type: ignore
                    del self.__unspent_outs[inp_id]
                # remove trx from unproccessed trxs
                del self.__unprocess_trxs[trx.id]

    def __block_assebmle_helper_data(self, blk: Block) -> None:
        for trx in blk.transactions:
            if not Utils.transaction_is_coinbase(trx):
                trx_inputs_data = {inp_id: self.unspent_outputs[inp_id] for inp_id in trx.inputs}
                # append inputs (for validation purposes)
                trx.inputs_data = trx_inputs_data # type: ignore

    def block_assemble_new(self, trxs_new: List[Transaction]) -> Block:
        logger.debug('assembling new block')
        # coinbase trx
        coinbase = Utils.coinbase_transaction()
        blk_new = Block(time(), self.__ledger[-1], [coinbase, *trxs_new])
        return blk_new

    def block_assemble_new_full(self) -> Block:
        return self.block_assemble_new([*self.unprocessed_transactions.values()])

    async def block_mine(self) -> Block:
        blk = self.block_assemble_new_full()
        return await self.__io_loop.run_in_executor(None, functools.partial(block_mine_internal, blk))

    def external_miner_start(self, addr: PeerAddr) -> None:
        self.__ext_miner = ExternalMiner(self.__io_loop, addr, self.block_assemble_new_full)

    async def block_mine_external(self) -> Block:
        return await self.__ext_miner.block_mine()

    def command_greet_handler(self, height: int, to_addr: PeerAddr) -> None:
        logger.debug(f'command_greet_handler {height} {to_addr}')
        if height != self.last_block.height:
            blocks_to_send = [blk for blk in self.__ledger if blk.height > height]
            self.__io_loop.create_task(self.command_send(to_addr, InfoCommand(blocks_to_send)))

    def command_info_handler(self,  blocks_insert: List[JsonDict]) -> None:
        logger.debug(f'command_info_handler {blocks_insert}')
        #merge blockchains parts
        blks_m = [Block.unserialize(blk_str) for blk_str in blocks_insert]
        head_idx = -1
        for i in range(len(blks_m)):
            try:
                Rules.block_valid(self.__ledger[-1], blks_m[i])
                #have head for merging
                head_idx = i
                break
            except (BlockRulesError, TransactionRulesError):
                pass
        if head_idx < 0 or head_idx > 10:
            logger.error('possible fork')
            return
        for i in range(head_idx, len(blks_m)):
            self.block_add_to_blockchain(blks_m[i])


    @property
    def unprocessed_transactions(self) -> Dict[TransactionID, Transaction]:
        return self.__unprocess_trxs
    @property
    def unspent_outputs(self) -> Dict[OutputID, Output]:
        return self.__unspent_outs
    @property
    def last_block(self) -> Block:
        return self.__ledger[-1]

    def block_at_height(self, height: int) -> Block:
        return [blk for blk in self.__ledger if blk.height == height][0]
