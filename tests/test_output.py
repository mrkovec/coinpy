import unittest
# from json import loads as JSONloads

from .test_setup import *

from coinpy.core.output import Output


class TestOutputMethods(unittest.TestCase):
    def setUp(self) -> None:
        self.outp = Output(100, TEST_PUBADDR)

    def test_from_json_obj(self) -> None:
        outp_new = Output.from_json(self.outp.to_json())
        self.assertIsInstance(outp_new, Output)
        self.assertIs(type(outp_new), Output)
        self.assertTrue(self.outp.id == outp_new.id)

if __name__ == '__main__':
    unittest.main()
