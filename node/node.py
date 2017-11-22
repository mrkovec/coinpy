from typing import List, Iterator, Dict, Optional
import logging
import socket
import sys
import multiprocessing
import queue
from time import time
import os

import json

from coinpy.core.block import Block, GENESIS_BLOCK
from coinpy.core.output import Output, OutputID
from coinpy.core.transaction import Transaction, CoinbaseTransaction, TransactionID
from coinpy.core.crypto import Pubaddr, PrivkeyStorage
from coinpy.core.errors import TransactionRulesError

from .consensus import Rules


# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Node(object):
    def __init__(self) -> None:
        Rules.block_valid_difficulty(GENESIS_BLOCK)
        self.__ledger: List[Block] = [GENESIS_BLOCK]
        self.__unprocess_trxs: Dict[TransactionID, Transaction] = {}
        self.__unspent_outs: Dict[OutputID, Output] = {}

        self.__mined_block = multiprocessing.Queue(1)



    def validate_block(self, blk: Block) ->None:
        # consensus
        Rules.block_valid(self.__ledger[-1], blk)
        # valid blocks transactions and inputs
        for trx_id in blk.trxs:
            trx = blk.trxs_data[trx_id]

            if type(trx) is CoinbaseTransaction:
                return

            if trx_id not in self.__unprocess_trxs:
                raise TransactionRulesError('unknown trx')
            for inp_id in trx.inputs:
                if inp_id not in self.__unspent_outs:
                    raise TransactionRulesError('spent output as input')

    def process_block(self, blk: Block) ->None:
        for trx_id in blk.trxs:
            for unspout in blk.trxs_data[trx_id].outputs:
                # add trx outputs into unspent outputs
                self.__unspent_outs[unspout.id] = unspout
            if type(blk.trxs_data[trx_id]) is not CoinbaseTransaction:
                for inp_id in blk.trxs_data[trx_id].inputs:
                    # delete trx inputs from unspent outputs
                    del self.__unspent_outs[inp_id]
                # remove trx from unproccessed trxs
                del self.__unprocess_trxs[trx_id]

    def add_block(self, blk_new: Block) -> None:
        logger.debug(f'new block {blk_new.id}')
        self.validate_block(blk_new)
        self.process_block(blk_new)
        self.__ledger.append(blk_new)

    def assemble_block(self, trxs_new: Dict[TransactionID, Transaction]) -> Block:
        # coinbase trx
        coinbase_outp = Output(10, Pubaddr(b''))
        coinbase = CoinbaseTransaction(time(), [], [coinbase_outp])
        # sign coinbase trx with default privkey
        sk = PrivkeyStorage.load_signing_keys()
        # coinbase.sign(list(self.__signing_keys.values())[0])
        coinbase.sign(sk['default'])

        blk_trxs_data = {}
        for _, trx in trxs_new:
            trx_inputs_data = {inp_id: self.__unspent_outs[inp_id] for inp_id in trx.inputs}
            # append inputs (for validation purposes)
            trx.inputs_data = trx_inputs_data
            blk_trxs_data[trx.id] = trx

        coinbase.inputs_data = {}
        blk_trxs_data[coinbase.id] = coinbase

        # assemble trxs into block
        blk_new = Block(time(), self.__ledger[-1], [*blk_trxs_data.keys()])
        # append full trx data to block data for validation purposes
        blk_new.trxs_data = blk_trxs_data
        # append inputs (for validation purposes)
        return blk_new

    # def mining_manager(self) -> Iterator[int]:
    def mining_manager(self) -> Iterator[int]:
        miners = []
        for w in range(1):
            blk = self.assemble_block(self.__unprocess_trxs)
            miner = Miner(blk, self.__mined_block)
            p = multiprocessing.Process(target=miner.run, daemon=True)
            p.start()
            miners.append(p)

        while True:
            try:
                blk_new = self.__mined_block.get_nowait()
                # logger.debug(f'new block {blk_new}')
                logger.info(f'new block mined {blk_new.id}')
                for m in miners:
                    m.terminate()
                self.add_block(blk_new)
                return
            except queue.Empty:
                pass
            except Exception as e:
                logger.exception(str(e))
            yield 1

    @property
    def unprocessed_trxs(self) -> Dict[TransactionID, Transaction]:
        return self.__unprocess_trxs


class Miner(object):
    def __init__(self, blk: Block, mbq:  multiprocessing.Queue = None ) -> None:
        self.__mbq = mbq
        self.__blk = blk

    def run(self) -> Block:
        while True:
            try:
                Rules.block_valid_difficulty(self.__blk)
                if self.__mbq is not None:
                    self.__mbq.put(self.__blk)
                return self.__blk
            except Exception as e:
                pass
            self.__blk.nonce += 1


class Scheduler(object):
    def __init__(self, gen: List[Iterator[int]] = []) -> None:
        self.active: List[Iterator[int]] = gen
        self.scheduled: List[Iterator[int]] = []

    def add_microthread(self, gen: Iterator[int]) -> None:
        self.active.append(gen)

    def run(self) -> Iterator[int]:
        while True:
            if len(self.active) == 0:
                return
            for thread in self.active:
                try:
                    next(thread)
                    self.scheduled.append(thread)
                except StopIteration:
                    pass
                yield 1
            self.active, self.scheduled = self.scheduled, []
