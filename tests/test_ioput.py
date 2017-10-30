# import unittest
# from json import loads as json_loads
#
# from .__setpaths__ import *
# from coinpy.core.ioput import IOput
#
# class TestIOputMethods(unittest.TestCase):
#     def setUp(self):
#         self.input = IOput(100, 'a', 'b')
#
#     def test_from_json_obj(self):
#         new_ioput = IOput.from_obj(json_loads(self.input.to_json()))
#         self.assertIsInstance(new_ioput, IOput)
#         self.assertIs(type(new_ioput), IOput)
#         self.assertTrue(self.input.verify_hash(new_ioput.id))
#
# if __name__ == '__main__':
#     unittest.main()
