from typing import List, Iterator, Dict, Optional, Any
import logging
# import socket
import sys
import multiprocessing
import queue
from time import time
import asyncio
import os
# import uuid

import json

from coinpy.core.block import Block, GENESIS_BLOCK
from coinpy.core.output import Output, OutputID
from coinpy.core.transaction import Transaction, TransactionID, Utils
from coinpy.core.crypto import Pubaddr, PrivkeyStorage, ID
from coinpy.core.errors import TransactionRulesError

from .consensus import Rules
from .miner import Miner, ExternalMiner
from .peer import Peer, PeerAddr
from .commands import GreetCommand, ReplyGreetCommand, AnnounceBlockCommand, AnnounceTransactionCommand
# import coinpy.node.peer as peer
# import coinpy.node.commands as commands

logger = logging.getLogger(__name__)

class Node(object):
    def __init__(self, loop: asyncio.AbstractEventLoop, **config: Any) -> None:
        logger.info(f'starting node with {config}')
        Rules.block_valid_difficulty(GENESIS_BLOCK)
        self.__ledger: List[Block] = [GENESIS_BLOCK]
        self.__unprocess_trxs: Dict[TransactionID, Transaction] = {}
        self.__unspent_outs: Dict[OutputID, Output] = {}
        self.__mined_block_queue = multiprocessing.Queue(1) # type: ignore

        self.__io_loop = loop
        self.__config = config

        self.__peer = Peer(self.__config.get('addr', PeerAddr(('127.0.0.1', 50001))), self.__io_loop)
        self.__peer.neighbors_add(self.__config.get('neighbors', []))
        # self.__peer.register_commnads([(self, AnnounceTransactionCommand), (self, AnnounceBlockCommand)])
        self.__peer.commnads_register([(self, GreetCommand), (self, AnnounceBlockCommand)])

        self.__procblk_task = self.__io_loop.create_task(self.block_await())

        self.__generate_blocks = self.__config.get('gen', 0)
        self.__miners: List[multiprocessing.Process] = []
        # self.block_mining_start()
        self.__extminer_task = self.__io_loop.create_task(self.block_external_mining_start(PeerAddr(('127.0.0.1', 4040))))



        # self.__peer.commnad_send_bulk(GreetCommand(self.__ledger[-1].height))

    def stop(self) -> None:
        logger.info('stopping node')
        self.block_mining_stop()
        self.__procblk_task.cancel()
        self.__peer.stop()

    def block_add(self, blk_new: Block) -> None:
        logger.debug(f'adding block {blk_new.id}')
        self.block_mining_stop()
        try:
            self.block_assebmle_helper_data(blk_new)
            self.block_validate(blk_new)
            self.block_proccess(blk_new)
            self.__ledger.append(blk_new)
            self.__peer.commnad_send_bulk(AnnounceBlockCommand(blk_new))
        except Exception as e:
            logger.debug(f'consensus error {str(e)}')
            # logger.exception(str(e))
        self.block_mining_start()

    def block_validate(self, blk: Block) -> None:
        logger.debug(f'validating block {blk.id}')
        # consensus
        Rules.block_valid(self.__ledger[-1], blk)
        # valid blocks transactions and inputs
        for trx in blk.transactions:
            if Utils.transaction_is_coinbase(trx):
                return
            # if trx_id not in self.__unprocess_trxs:
            #     raise TransactionRulesError('unknown trx')
            for inp_id in trx.inputs:
                if inp_id not in self.__unspent_outs:
                    raise TransactionRulesError('spent output as input')

    def block_proccess(self, blk: Block) -> None:
        logger.debug(f'proccessing block {blk.id}')
        for trx in blk.transactions:
            for unspout in trx.outputs: # type: ignore
                # add trx outputs into unspent outputs
                self.__unspent_outs[unspout.id] = unspout
            if not Utils.transaction_is_coinbase(trx):
                for inp_id in trx.inputs: # type: ignore
                    del self.__unspent_outs[inp_id]
                # remove trx from unproccessed trxs
                # del self.__unprocess_trxs[trx_id]
                del self.__unprocess_trxs[trx.id]

    def block_assebmle_helper_data(self, blk: Block) -> None:
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

    async def block_await(self) -> None:
        while True:
            try:
                blk_new = self.__mined_block_queue.get_nowait()
                logger.debug(f'mined new block {blk_new}')
                self.block_add(blk_new)

            except queue.Empty:
                await asyncio.sleep(1, loop=self.__io_loop)
            except asyncio.CancelledError:
                return
            except Exception as e:
                logger.exception(str(e))

    def block_mining_start(self) -> None:
        for _ in range(self.__generate_blocks):
            blk = self.block_assemble_new([*self.unprocessed_transactions.values()])
            miner = Miner(blk, self.__mined_block_queue)
            p = multiprocessing.Process(target=miner.run, daemon=True)
            p.start()
            logger.debug(f'starting mining process {p}')
            self.__miners.append(p)

    async def block_external_mining_start(self, addr: PeerAddr) -> None:
        ext_miner = ExternalMiner(self.__io_loop, addr, self.__mined_block_queue, self.block_assemble_new_full)
        await ext_miner.run()
    #     p = multiprocessing.Process(target=ext_miner.run, daemon=True)
    #     p.start()
    #     logger.debug(f'starting external mining process {p}')
    #     self.__miners.append(p)

    def block_mining_stop(self) -> None:
        for p in self.__miners:
            p.terminate()
            logger.debug(f'terminating mining process {p}')
        self.__miners = []


    def command_greet(self, height:int, from_addr: PeerAddr) -> None:
        if self.__ledger[-1].height > height:
            self.__peer.command_send(from_addr, ReplyGreetCommand(self.__ledger[-1].height))

    def command_replygreet(self) -> None:
        pass

    @property
    def unprocessed_transactions(self) -> Dict[TransactionID, Transaction]:
        return self.__unprocess_trxs
    @property
    def unspent_outputs(self) -> Dict[OutputID, Output]:
        return self.__unspent_outs


    # def start(self, run = False) -> None:
    #     self.__peer.start()
    #     if run:
    #         try:
    #             self.io_loop.run_until_complete(self.process_msg())
    #         except KeyboardInterrupt:
    #             pass
    #         self.stop()
    # def stop(self) -> None:
    #     # self.__peer.stop()
    #     self.io_loop.close()
