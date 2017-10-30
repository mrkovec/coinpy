import unittest

from .test_setup import *

from coinpy.core.output import Output
from coinpy.core.trans import Trans
from coinpy.core.block import (
    Block, BlockID
)

class TestBlockMethods(unittest.TestCase):
    def setUp(self) -> None:
        trx = Trans(123)
        trx.add_inp(Output(100, TEST_PUBADDR).id)
        trx.add_outp(Output(10, TEST_PUBADDR))
        trx.add_outp(Output(90, TEST_PUBADDR))
        prev_blk = Block(123)
        self.blk = Block(345, prev_blk)
        self.blk.add_trx(trx.id)

    def test_blk_from_json_obj(self) -> None:
        blk_new = Block.from_json(self.blk.to_json())
        self.assertIsInstance(blk_new, Block)
        self.assertIs(type(blk_new), Block)
        self.assertTrue(blk_new.id == self.blk.id)

# import unittest
# from json import loads as json_loads
#
# from .__setpaths__ import *
#
# from coinpy.core.ioput import IOput, KEY_VALUE, KEY_FROM_ADDR, KEY_TO_ADDR
# from coinpy.core.trans import Trans, KEY_TIME_STAMP, KEY_INPS, KEY_OUTPS
# from coinpy.core.block import Block, KEY_PREV_BLOCK, KEY_TRXS
#
# class TestBlockMethods(unittest.TestCase):
#     def setUp(self):
#         trx = Trans(123)
#         trx.add_inp(IOput(100, 'a', 'b'))
#         trx.add_outp(IOput(10, 'b', 'c'))
#         trx.add_outp(IOput(90, 'b', 'b'))
#         self.block = Block(345)
#         self.block.add_trx(trx)
#
#     def test_blk_from_json_obj(self):
#         new_blk = Block.from_obj(json_loads(self.block.to_json()))
#         self.assertIsInstance(new_blk, Block)
#         self.assertIs(type(new_blk), Block)
#         self.assertTrue(self.block.verify_hash(new_blk.id))
#
#
#
#
#
# if __name__ == '__main__':
#     unittest.main()
