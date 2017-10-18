import unittest
import json

import __setpaths__

from coinpy.core.ioput import IOput, KEY_VALUE, KEY_FROM_ADDR, KEY_TO_ADDR
# from core.errors import Error

class TestIOputMethods(unittest.TestCase):
    def setUp(self):
        self.input = IOput(100, 'a', 'b')

    def test_prepare_data(self):
        self.assertEqual(self.input._prepare_data(), {KEY_VALUE: 100, KEY_FROM_ADDR: "a", KEY_TO_ADDR: "b"})

    def test_from_json_obj(self):
        json_obj = {"jX8Z/UvTi+GO6i8jN6/XVkHI1eFW3TZCj9r/ATmma1sJ5g7kA8legR0zj12zbJehcx1d4teE8QNTx+RBlEepnw==": {KEY_VALUE: 100, KEY_FROM_ADDR: "a", KEY_TO_ADDR: "b"}}
        new_ioput = IOput.from_json_obj(json_obj)
        self.assertIsInstance(new_ioput, IOput)
        self.assertIs(type(new_ioput), IOput)



    # def test_to_json(self):
    #     self.assertEqual(self.input.to_json(),
    #         '''{{"782f9fe2150282489ab3b6cb6b473969a53de5e4e6840e38840c3df7245228f8": '''
    #         '''{{"{}": 100, "{}": "a", "{}": "b"}}}}'''.format(KEY_VALUE, KEY_FROM_ADDR, KEY_TO_ADDR))
    #
    # def test_check_hash(self):
    #      self.assertTrue(self.input.check_hash(
    #         '782f9fe2150282489ab3b6cb6b473969a53de5e4e6840e38840c3df7245228f8'))
    #
    # def test_ioput_from_json(self):
    #     new_ioput = IOput.from_json_obj(json.loads(self.input.to_json()))
    #     self.assertIsInstance(new_ioput, IOput)
    #     self.assertIs(type(new_ioput), IOput)

    # def test_ioput_from_json_bad_hash(self):
    #     with self.assertRaises(Error):
    #         IOput.from_json_obj(json.loads(
    #             '''{{"abc": '''
    #             '''{{"{}": 100, "{}": "a", "{}": "b"}}}}'''.format(KEY_VALUE, KEY_FROM_ADDR, KEY_TO_ADDR)))
    #
    # def test_ioput_from_json_bad_data(self):
    #     with self.assertRaises(Error):
    #         IOput.from_json_str(
    #             '''{{"782f9fe2150282489ab3b6cb6b473969a53de5e4e6840e38840c3df7245228f8": '''
    #             '''{{"{}": 100, "{}": "a", "{}": "b"}}}}'''.format('bad_key', KEY_FROM_ADDR, KEY_TO_ADDR))
    #
    # def test_ioput_from_json_bad_json(self):
    #     with self.assertRaises(Error):
    #         IOput.from_json_str(
    #             '''"782f9fe2150282489ab3b6cb6b473969a53de5e4e6840e38840c3df7245228f8": '''
    #             '''{{"{}": 100, "{}": "a", "{}": "b"}}}}'''.format(KEY_VALUE, KEY_FROM_ADDR, KEY_TO_ADDR))

if __name__ == '__main__':
    unittest.main()
