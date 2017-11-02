import unittest
# from json import loads as JSONloads

from .setup import *

from coinpy.core.output import Output
from coinpy.core.crypto import Serializable


class TestOutputMethods(unittest.TestCase):
    def setUp(self) -> None:
        self.outp = Output(100, TEST_PUBADDR)

    def test_from_json_obj(self) -> None:
        outp_new = Output.unserialize_json(str(self.outp))
        self.assertIsInstance(outp_new, Serializable)
        self.assertIsInstance(outp_new, Output)
        self.assertIs(type(outp_new), Output)
        self.assertTrue(self.outp.id == outp_new.id)

if __name__ == '__main__':
    unittest.main()
