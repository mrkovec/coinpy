import unittest
import json

from .__setpaths__ import *
from coinpy.core.ioput import IOput, KEY_VALUE, KEY_FROM_ADDR, KEY_TO_ADDR

class TestIOputMethods(unittest.TestCase):
    def setUp(self):
        self.input = IOput(100, 'a', 'b')

    def test_from_json_obj(self):
        new_ioput = IOput.from_obj(JSON_OBJ)
        self.assertIsInstance(new_ioput, IOput)
        self.assertIs(type(new_ioput), IOput)

JSON_OBJ = {
    "jX8Z/UvTi+GO6i8jN6/XVkHI1eFW3TZCj9r/ATmma1sJ5g7kA8legR0zj12zbJehcx1d4teE8QNTx+RBlEepnw==":
    {
        KEY_VALUE: 100,
        KEY_FROM_ADDR: "a",
        KEY_TO_ADDR: "b"
    }
}

if __name__ == '__main__':
    unittest.main()
