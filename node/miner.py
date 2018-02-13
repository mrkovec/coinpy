from typing import List
import multiprocessing
import logging
from time import time

from coinpy.core.block import Block
from .consensus import Rules
logger = logging.getLogger(__name__)

class Miner(object):
    def __init__(self, blk: Block, mbq:  multiprocessing.Queue = None ) -> None:
        self.__mbq = mbq
        self.__blk = blk

    def run(self) -> Block:
        # logger.info(f'mining block {self.__blk}')
        ts = time()
        while True:
            try:
                Rules.block_valid_difficulty(self.__blk)
                if self.__mbq is not None:
                    self.__mbq.put(self.__blk)
                logger.info(f'block {self.__blk} mined in {time()-ts}s')
                return self.__blk
            except Exception as e:
                pass
            self.__blk.nonce += 1


# class Scheduler(object):
#     def __init__(self, gen: List[Iterator[int]] = []) -> None:
#         self.active: List[Iterator[int]] = gen
#         self.scheduled: List[Iterator[int]] = []
#
#     def add_microthread(self, gen: Iterator[int]) -> None:
#         self.active.append(gen)
#
#     def run(self) -> Iterator[int]:
#         while True:
#             if len(self.active) == 0:
#                 return
#             for thread in self.active:
#                 try:
#                     next(thread)
#                     self.scheduled.append(thread)
#                 except StopIteration:
#                     pass
#                 yield 1
#             self.active, self.scheduled = self.scheduled, []
