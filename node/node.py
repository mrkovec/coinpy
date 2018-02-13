from typing import List, Iterator, Dict, Optional, Any
import logging
# import socket
import sys
import multiprocessing
import queue
from time import time
import asyncio
import os

import json

from coinpy.core.block import Block, GENESIS_BLOCK
from coinpy.core.output import Output, OutputID
from coinpy.core.transaction import Transaction, CoinbaseTransaction, TransactionID
from coinpy.core.crypto import Pubaddr, PrivkeyStorage
from coinpy.core.errors import TransactionRulesError

from .consensus import Rules
from .miner import Miner
from .peer import Peer, PeerAddr
from .commands import AnnounceBlockCommand, NewTransactionCommand
# import coinpy.node.peer as peer
# import coinpy.node.commands as commands

logger = logging.getLogger(__name__)

class Node(object):
    def __init__(self, loop: asyncio.AbstractEventLoop, **config: Any) -> None:
        logger.info(f'starting node as {config}')
        Rules.block_valid_difficulty(GENESIS_BLOCK)
        self.__ledger: List[Block] = [GENESIS_BLOCK]

        self.__trxs: Dict[TransactionID, Transaction] = {}
        self.__unprocess_trxs: Dict[TransactionID, Transaction] = {}
        self.__unspent_outs: Dict[OutputID, Output] = {}

        self.__mined_block_queue = multiprocessing.Queue(1) # type: ignore

        self.__io_loop = loop
        self.__config = config

        self.__peer = Peer(self.__config.get('addr', PeerAddr(('127.0.0.1', 50001))), self.__io_loop)
        self.__peer.add_neighbors(self.__config.get('neighbors', []))
        self.__peer.register_commnads([(self, NewTransactionCommand), (self, AnnounceBlockCommand)])

    def stop(self) -> None:
        logger.info(f'stopping node')
        self.__peer.stop()


    # async def get_transaction(self, trx_id: TransactionID) -> Transaction:
    #     while True:
    #         try:
    #             return self.unprocessed_transactions[trx_id]
    #         except KeyError:
    #             await asyncio.sleep(5, loop=self.__io_loop)
    #         except Exception as e:
    #             logger.exception(str(e))
    #
    #
    # def check_validation_data(self, blk: Block) -> None:
    #     for trx_id in blk.transactions
    #         try:
    #             blk.trxs_data
    #         except AttributeError:
    def add_transaction(self, trx_new: Transaction) -> None:
        if trx_new.id in self.__unprocess_trxs or trx_new.id in self.__trxs:
            logger.debug(f'transaction {trx_new.id} {trx_new} already added')
        else:
            logger.debug(f'adding transaction {trx_new.id} {trx_new}')
            Rules.transaction_valid_header(trx_new)
            self.__unprocess_trxs[trx_new.id] = trx_new


    def add_block(self, blk_new: Block) -> None:
        logger.debug(f'adding block {blk_new.id} {blk_new}')
        self.validate_block(blk_new)
        self.proccess_block(blk_new)
        self.__ledger.append(blk_new)

    def validate_block(self, blk: Block) -> None:
        logger.debug('validating block')
        # consensus
        Rules.block_valid(self.__ledger[-1], blk)
        # valid blocks transactions and inputs
        for trx_id in blk.transactions:
            trx = blk.trxs_data[trx_id] # type: ignore
            if type(trx) is CoinbaseTransaction:
                return
            if trx_id not in self.__unprocess_trxs:
                raise TransactionRulesError('unknown trx')
            for inp_id in trx.inputs:
                if inp_id not in self.__unspent_outs:
                    raise TransactionRulesError('spent output as input')

    def proccess_block(self, blk: Block) ->None:
        logger.debug('proccessing block')
        for trx_id in blk.transactions:
            for unspout in blk.trxs_data[trx_id].outputs: # type: ignore
                # add trx outputs into unspent outputs
                self.__unspent_outs[unspout.id] = unspout
            if type(blk.trxs_data[trx_id]) is not CoinbaseTransaction: # type: ignore
                for inp_id in blk.trxs_data[trx_id].inputs: # type: ignore
                    # delete trx inputs from unspent outputs
                    del self.__unspent_outs[inp_id]
                # remove trx from unproccessed trxs
                del self.__unprocess_trxs[trx_id]

    # def assebmle_helper_data(self, )

    
    def assemble_new_block(self, trxs_new: Dict[TransactionID, Transaction]) -> Block:
        # coinbase trx
        coinbase_outp = Output(10, Pubaddr(b''))
        coinbase = CoinbaseTransaction(time(), [], [coinbase_outp])
        # sign coinbase trx with default privkey
        sk = PrivkeyStorage.load_signing_keys()
        coinbase.sign(sk['default'])

        # assemble full trxs/inputs data into block
        blk_trxs_data = {}
        for trx in trxs_new.values():
            trx_inputs_data = {inp_id: self.unspent_outputs[inp_id] for inp_id in trx.inputs}
            # append inputs (for validation purposes)
            trx.inputs_data = trx_inputs_data # type: ignore
            blk_trxs_data[trx.id] = trx

        coinbase.inputs_data = {} # type: ignore
        blk_trxs_data[coinbase.id] = coinbase
        # assemble trxs into block
        blk_new = Block(time(), self.__ledger[-1], [*blk_trxs_data.keys()])
        # append full trx data to block data for validation purposes
        blk_new.trxs_data = blk_trxs_data # type: ignore
        return blk_new

    async def mine_block(self) -> None:
        miners = []
        for w in range(1):
            blk = self.assemble_new_block(self.unprocessed_transactions)
            miner = Miner(blk, self.__mined_block_queue)
            p = multiprocessing.Process(target=miner.run, daemon=True)
            p.start()
            miners.append(p)

        while True:
            try:
                blk_new = self.__mined_block_queue.get_nowait()
                for m in miners:
                    m.terminate()
                self.add_block(blk_new)
                self.__peer.send_bulk_commnad(AnnounceBlockCommand(blk_new))
                return
            except queue.Empty:
                await asyncio.sleep(1, loop=self.__io_loop)
            except Exception as e:
                logger.exception(str(e))

            # yield 1

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
