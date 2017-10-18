import unittest
import json

from .__setpaths__ import *

from coinpy.core.ioput import IOput, KEY_VALUE, KEY_FROM_ADDR, KEY_TO_ADDR
from coinpy.core.trans import Trans, KEY_TIME_STAMP, KEY_INPS, KEY_OUTPS

class TestTransMethods(unittest.TestCase):
    def setUp(self):
        self.trx = Trans(123)
        self.trx.add_inp(IOput(100, 'a', 'b'))
        self.trx.add_outp(IOput(10, 'b', 'c'))
        self.trx.add_outp(IOput(90, 'b', 'b'))

    def test_trx_from_json_obj(self):
        json_obj = {
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
        new_trx = Trans.from_json_obj(json_obj)
        self.assertIsInstance(new_trx, Trans)
        self.assertIs(type(new_trx), Trans)


if __name__ == '__main__':
    unittest.main()
