import unittest
import io

from .setup import *

from coinpy.core.output import Output
from coinpy.core.trans import Trans
from coinpy.core.block import (
    Block, BlockID, GENESIS_BLOCK
)
from coinpy.core.crypto import Privkey, Serializable

class TestBlockMethods(unittest.TestCase):
    def setUp(self) -> None:
        self.trx = Trans(123, [Output(100, TEST_PUBADDR).id], [Output(10, TEST_PUBADDR), Output(90, TEST_PUBADDR)])
        self.trx.sign(Privkey.from_pem(io.StringIO(PEM_FILE_DATA)))
        # prev_blk = Block(123,[])
        # print(bytes(GENESIS_BLOCK.id))
        self.blk = Block(345, GENESIS_BLOCK, [self.trx.id])
        # self.blk = Block(345, trxs = [self.trx.id])

        # self.blk.add_trx(trx.id)

    def test_blk_from_json_obj(self) -> None:
        pass
        # print(str(self.blk))
        blk_new = Block.unserialize_json(str(self.blk))
        # print(str(blk_new))
        self.assertIsInstance(blk_new, Serializable)
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
