import unittest
import io
from time import time

from .setup import *

from coinpy.core.output import Output
from coinpy.core.transaction import Transaction
from coinpy.core.block import (
    Block, BlockID, GENESIS_BLOCK, GenesisBlock
)
from coinpy.core.crypto import Privkey, Serializable

from coinpy.node.consensus import Rules

class TestBlockMethods(unittest.TestCase):
    def setUp(self) -> None:
        self.trx = Transaction(123, [Output(100, TEST_PUBADDR).id], [Output(10, TEST_PUBADDR), Output(90, TEST_PUBADDR)])
        self.trx.sign(Privkey.from_pem(io.StringIO(PEM_FILE_DATA)))
        # self.blk = Block(345, GENESIS_BLOCK, [self.trx.id])
        self.blk = Block(345, GENESIS_BLOCK, [self.trx])

    def test_blk_from_json_obj(self) -> None:
        blk_new = Block.unserialize_json(str(self.blk))
        self.assertIsInstance(blk_new, Serializable)
        self.assertIsInstance(blk_new, Block)
        self.assertIs(type(blk_new), Block)
        self.assertTrue(blk_new.id == self.blk.id)


# class TestMineGenesisBlock(unittest.TestCase):
#     def test_mine_genesis_block(self) -> None:
#         n = 0
#         t = time()
#         dif = 3
#         while 1:
#             blk = GenesisBlock(dif, n, t)
#             try:
#                 Rules.block_valid_difficulty(blk)
#                 print('mined', bytes(blk.id))
#                 print(str(blk))
#                 print(time()-t)
#                 break
#             except:
#                 pass
#             n += 1

if __name__ == '__main__':
    unittest.main()
