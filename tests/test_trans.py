import unittest
import io

from .test_setup import *

from coinpy.core.crypto import Privkey
from coinpy.core.output import Output
from coinpy.core.trans import Trans


class TestTransMethods(unittest.TestCase):
    def setUp(self) -> None:
        self.trx = Trans(123, [Output(100, TEST_PUBADDR).id], [Output(10, TEST_PUBADDR), Output(90, TEST_PUBADDR)])
        self.trx.sign(Privkey.from_pem(io.StringIO(PEM_FILE_DATA)))


    def test_trx_from_json_obj(self) -> None:
        trx_new = Trans.from_json(self.trx.to_json())
        self.assertIsInstance(trx_new, Trans)
        self.assertIs(type(trx_new), Trans)
        self.assertTrue(trx_new.id == self.trx.id)





# JSON_OBJ = {
#    "4rD2KC73vKnGxWG9vCidOGrJxPc8Ruuu9pYg5z6GC6ZNHAfrgurSDJLbAz/yVR95S6dJrJgCtvRkfbButCryWg==":{
#       KEY_TIME_STAMP:123,
#       KEY_INPS:[
#          {
#             "jX8Z/UvTi+GO6i8jN6/XVkHI1eFW3TZCj9r/ATmma1sJ5g7kA8legR0zj12zbJehcx1d4teE8QNTx+RBlEepnw==":{
#                KEY_VALUE:100,
#                KEY_FROM_ADDR:"a",
#                KEY_TO_ADDR:"b"
#             }
#          }
#       ],
#       KEY_OUTPS:[
#          {
#             "oiklrkgJVZq1p5zR7pu8ecZPoR4vXB/kd6xjOIJOPiwPwCQa6O1jyWgmIRZY3Zi85aet8UYoX9wxwkNoc7in4g==":{
#                KEY_VALUE:10,
#                KEY_FROM_ADDR:"b",
#                KEY_TO_ADDR:"c"
#             }
#          },
#          {
#             "cYYvpgx+IksdERjNQ8eqXPzvEXTyey+Dhw2jNW6yeNZiKdsV2bWXTeU3J3ERe7AH1lx7zmFNxyS7cEo3cxYctw==":{
#                KEY_VALUE:90,
#                KEY_FROM_ADDR:"b",
#                KEY_TO_ADDR:"b"
#             }
#          }
#       ]
#    }
# }

# JSON_STR =
#     '''{{"782f9fe2150282489ab3b6cb6b473969a53de5e4e6840e38840c3df7245228f8": '''
#      '''{{"{}": 100, "{}": "a", "{}": "b"}}}}'''.format('bad_key', KEY_FROM_ADDR, KEY_TO_ADDR))

if __name__ == '__main__':
    unittest.main()
