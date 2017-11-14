from typing import List, Iterator, Dict, Optional
import logging
import socket
import sys
import multiprocessing
import queue
from time import time

import json

from coinpy.core.block import Block, GENESIS_BLOCK
from coinpy.core.output import Output, OutputID
from coinpy.core.trans import Trans, CoinbaseTrans, TransID
from coinpy.core.crypto import Privkey
from coinpy.core.errors import TransRulesError

from .consensus import Rules


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Node(object):
    def __init__(self) -> None:
        Rules.verify_difficulty(GENESIS_BLOCK)
        self.__ledger: List[Block] = [GENESIS_BLOCK]
        self.__unprocess_trxs: Dict[TransID, Trans] = {}
        self.__unspent_outs: Dict[OutputID, Output] = {}

        self.__mined_block = multiprocessing.Queue(1)
        self.__coinbase_sk = Privkey.new()


    def validate_block(self, blk: Block) ->None:
        for trx_id in blk.trxs:
            trx = blk.trx_dta[trx_id]
            if type(trx) is not CoinbaseTrans:
                if trx_id not in self.__unprocess_trxs:
                    raise TransRulesError('unknown trx')

                inp_pubaddrs = set()
                for inp_id in trx.inps:
                    if inp_id not in self.__unspent_outs:
                        raise TransRulesError('spent output as input')
                    inp = self.__unspent_outs[inp_id]
                    inp_pubaddrs.add(inp.pubaddr)

                if len(inp_pubaddrs) != 1:
                    raise TransRulesError('inputs from more than one address')

                if inp_pubaddrs.pop() !=  bytes(trx.signature_pubkey):
                    raise TransRulesError('non coresponding input address with trx signing key')
                trx.verify_sign()


    def process_block(self, blk: Block) ->None:
        for trx_id in blk.trxs:
            for unspout in blk.trx_dta[trx_id].outps:
                self.__unspent_outs[unspout.id] = unspout
            if type(blk.trx_dta[trx_id]) is not CoinbaseTrans:
                for inp_id in blk.trx_dta[trx_id].inps:
                    del self.__unspent_outs[inp_id]
                del self.__unprocess_trxs[trx_id]

    def add_block(self, blk_new: Block) -> None:
        Rules.valid_block(self.__ledger[-1], blk_new)
        self.validate_block(blk_new)
        self.process_block(blk_new)
        self.__ledger.append(blk_new)

    def assemble_block(self) -> Block:
        coinbase_outp = Output(10, self.__coinbase_sk.pubkey.pubaddr)
        coinbase = CoinbaseTrans(time(), [], [coinbase_outp])
        coinbase.sign(self.__coinbase_sk)

        blk_trx_data = dict(self.__unprocess_trxs)
        blk_trx_data[coinbase.id] = coinbase
        blk_new = Block(time(), self.__ledger[-1], [*blk_trx_data.keys()])
        blk_new.trx_dta = blk_trx_data
        return blk_new

    # def mining_manager(self) -> Iterator[int]:
    def mining_manager(self) -> Iterator[int]:
        miners = []
        for w in range(1):
            blk = self.assemble_block()
            miner = Miner(self.__mined_block, blk)
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


class Miner(object):
    def __init__(self, mbq:  multiprocessing.Queue, blk: Block) -> None:
        # logger.debug(f'mining {blk}')
        self.__mbq = mbq
        self.__blk = blk

    def run(self) -> None:
        while True:
            try:
                Rules.verify_difficulty(self.__blk)
                self.__mbq.put(self.__blk)
                # logger.debug('minier exit')
                return
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
