import unittest
import io

from .setup import *

from coinpy.core.crypto import (
    Privkey, Serializable
)
from coinpy.core.output import Output
from coinpy.core.trans import Trans


class TestTransMethods(unittest.TestCase):
    def setUp(self) -> None:
        self.trx = Trans(123, [Output(100, TEST_PUBADDR).id], [Output(10, TEST_PUBADDR), Output(90, TEST_PUBADDR)])
        self.trx.sign(Privkey.from_pem(io.StringIO(PEM_FILE_DATA)))

    def test_trx_from_json_obj(self) -> None:
        trx_new = Trans.unserialize_json(str(self.trx))
        self.assertIsInstance(trx_new, Serializable)
        self.assertIsInstance(trx_new, Trans)
        self.assertIs(type(trx_new), Trans)
        self.assertTrue(trx_new.id == self.trx.id)


if __name__ == '__main__':
    unittest.main()
