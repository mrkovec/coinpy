from typing import List

from coinpy.core.block import Block, GENESIS_BLOCK
from coinpy.core.output import Output
from coinpy.core.trans import Trans

from .consensus import Rules

class Node(object):
    def __init__(self) -> None:
        Rules.verify_block_data(GENESIS_BLOCK)
        self.__ledger: List[Block] = [GENESIS_BLOCK]
        self.__unspouts: List[Output] = []
        self.__freetrxs: List[Trans] = []

    def add_block(self, blk_new: Block) -> None:
        Rules.valid_block(self.__ledger[-1], blk_new)
        self.__ledger.append(blk_new)

    def assemble_block(self) -> None:
        pass
