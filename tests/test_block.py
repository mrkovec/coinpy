import unittest
import json

import __setpaths__

from coinpy.core.ioput import IOput, KEY_VALUE, KEY_FROM_ADDR, KEY_TO_ADDR
from coinpy.core.trans import Trans, KEY_TIME_STAMP, KEY_INPS, KEY_OUTPS
from coinpy.core.block import Block, KEY_PREV_BLOCK, KEY_TRXS

class TestBlockMethods(unittest.TestCase):
    def setUp(self):
        trx = Trans(123)
        trx.add_inp(IOput(100, 'a', 'b'))
        trx.add_outp(IOput(10, 'b', 'c'))
        trx.add_outp(IOput(90, 'b', 'b'))
        self.block = Block('abc', 345)
        self.block.add_trx(trx)

    def test_blk_from_json_obj(self):
        pass
        json_obj = {
           "Kt4gS3gfUeb6KWn8f1VFAx4yvB6VZyNWIETHXPb86bkCOLw6rbU8LdAwYgpipDLmkg7mZbmAW9rdtbipYoOymw==":{
              KEY_TIME_STAMP:345,
              KEY_PREV_BLOCK:"abc",
              KEY_TRXS:[
                 {
                    "4rD2KC73vKnGxWG9vCidOGrJxPc8Ruuu9pYg5z6GC6ZNHAfrgurSDJLbAz/yVR95S6dJrJgCtvRkfbButCryWg==":{
                       KEY_TIME_STAMP:123,
                       KEY_INPS:[
                          {
                             "jX8Z/UvTi+GO6i8jN6/XVkHI1eFW3TZCj9r/ATmma1sJ5g7kA8legR0zj12zbJehcx1d4teE8QNTx+RBlEepnw==":{
                                KEY_VALUE:100,
                                KEY_FROM_ADDR:"a",
                                KEY_TO_ADDR:"b"
                             }
                          }
                       ],
                       KEY_OUTPS:[
                          {
                             "oiklrkgJVZq1p5zR7pu8ecZPoR4vXB/kd6xjOIJOPiwPwCQa6O1jyWgmIRZY3Zi85aet8UYoX9wxwkNoc7in4g==":{
                                KEY_VALUE:10,
                                KEY_FROM_ADDR:"b",
                                KEY_TO_ADDR:"c"
                             }
                          },
                          {
                             "cYYvpgx+IksdERjNQ8eqXPzvEXTyey+Dhw2jNW6yeNZiKdsV2bWXTeU3J3ERe7AH1lx7zmFNxyS7cEo3cxYctw==":{
                                KEY_VALUE:90,
                                KEY_FROM_ADDR:"b",
                                KEY_TO_ADDR:"b"
                             }
                          }
                       ]
                    }
                 }
              ]
           }
        }
        new_blk = Block.from_json_obj(json_obj)
        self.assertIsInstance(new_blk, Block)
        self.assertIs(type(new_blk), Block)

if __name__ == '__main__':
    unittest.main()
