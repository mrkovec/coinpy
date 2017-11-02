import unittest
import io

from .setup import *

# from coinpy.core.crypto import Hash, SerializableObject, SerializableObjectEncoder, Privkey, Pubkey
from coinpy.core.crypto import (
    Privkey, Pubkey
)
# from coinpy.core.errors import (
#     HashError, DataError
# )


# class TestSerializableObjectEncoder(unittest.TestCase):
#     def setUp(self):
#         self.ser_obj = Serializable(1)
#         self.not_ser_obj = NotSerializable(1)
#         self.not_impl_obj = NotImplemented(1)
#
#     def test_encode_serializable(self):
#         json_str = self.ser_obj.to_json()
#         new_obj = Serializable(-1)
#         new_obj.verify_and_unserialize_json(json_str)
#         self.assertTrue(self.ser_obj.verify_hash(new_obj.id))
#
#     def test_encode_not_serializable(self):
#         with self.assertRaises(DataError):
#             SerializableObjectEncoder().encode(self.not_ser_obj)
#
#     def test_encode_not_implemented(self):
#         with self.assertRaises(DataError):
#             SerializableObjectEncoder().encode(self.not_impl_obj)
#         with self.assertRaises(DataError):
#             self.not_impl_obj.verify_and_unserialize_json(self.ser_obj.to_json())
#
#     def test_encode_incorrect_data(self):
#         with self.assertRaises(DataError):
#             self.ser_obj.verify_and_unserialize_json('{"data":}')
#
#     def test_encode_incorrect_hash(self):
#         with self.assertRaises(HashError):
#             self.ser_obj.verify_and_unserialize_json('{"byPSfDifG8auTAa69VrNIm46XUIy4sLUiflTBHlKwDjnxOAANwKUPNBB2C4VAC9AOf0Jnff/OVnd0dMWLtz3Dw==": {"data": 1}}')


class TestPrivkey(unittest.TestCase):
    def test_from_pem_and_sign(self) -> None:
        sk = Privkey.from_pem(io.StringIO(PEM_FILE_DATA))
        _, sgn = sk.sign(b'abc')
        self.assertTrue(sk.pubkey.verify(sgn, b'abc'))

class TestPubkey(unittest.TestCase):
    def setUp(self) -> None:
        self.sk = Privkey.from_pem(io.StringIO(PEM_FILE_DATA))
        _, self.sgn = self.sk.sign(b'abc')

    def test_from_str(self) -> None:
        vk = TEST_PUBKEY
        self.assertTrue(vk.verify(self.sgn, b'abc'))



#
#     def test_str(self):
#         vk = Pubkey.from_str(self.sk.pubkey.str_)
#         self.assertTrue(vk.verify(self.sgn, 'abc'))
#
#     def test_address(self):
#         vk = self.sk.pubkey
#         self.assertTrue(self.sk.pubkey.verify_address('lZXmclFER25cE5WRjMuWQaz2g2MzFMat'))
#         with self.assertRaises(DataError):
#             self.sk.pubkey.verify_address('lZXmclFER25cE5WRjMuWQaz2g2MzFMax')
#
#
#
# class Serializable(SerializableObject, object_hash = Hash.new(64, b'test')):
#     def __init__(self, data: int) -> None:
#         self.data = data
#     def _serialize(self) -> object:
#         return {'data': self.data}
#     def _unserialize(self, obj_data: object) -> None:
#         self.data = obj_data['data']
#
#
# class NotSerializable():
#     def __init__(self, data: int) -> None:
#         self.data = data
#
#
# class NotImplemented(SerializableObject, object_hash = Hash.new(64, b'test')):
#     def __init__(self, data: int) -> None:
#         self.data = data





# class TestCryptoFunctions(unittest.TestCase):
#     def test_hash_from_str(self):
#         self.assertEqual(hash_from_str('123').get_str(), 'xeDkbtzK6Y8gXoXVde+XuKnJ3ICVbUtkFZFHZQeI2jDEls0cNTCuqDMg1LcEcNtRFoUx26+ZZlKG6UMquoNEUw==')

# class TestHashMethods(unittest.TestCase):
#     def test_hash_from_str(self):
#         self.assertEqual(hash_from_str('123').get_str(), 'xeDkbtzK6Y8gXoXVde+XuKnJ3ICVbUtkFZFHZQeI2jDEls0cNTCuqDMg1LcEcNtRFoUx26+ZZlKG6UMquoNEUw==')
#
#     def test_hash_from_obj(self):
#         self.assertEqual(hash_from_obj({'a': '123'}).get_str(), 'ECJWUv8efAIKb9sbtupyPi+/qJgwU4SBuajYbrMZ74pABzeT3km7zEB8HyLYurAu9aLMkDtqOoOYdrDfiFobwQ==')
#
#
# class TestCryptoObjMethods(unittest.TestCase):
#     def setUp(self):
#         self.input = IOput(-1, '', '')
#
#     def test_process_verify_obj_incorrect_hash(self):
#         with self.assertRaises(HashError):
#             self.input.process_verify_obj(OBJ_INCORRECT_HASH)
#
#     def test_process_verify_obj_incorrect_data(self):
#         with self.assertRaises(DataError):
#             self.input.process_verify_obj(OBJ_BAD_KEY)
#
#     def test_process_verify_json(self):
#         self.input.process_verify_json(JSON_STR)
#         self.assertEqual(self.input._prepare_data(), {KEY_VALUE: 100, KEY_FROM_ADDR: "a", KEY_TO_ADDR: "b"})
#
#
#     def test_process_verify_json_incorrect_data(self):
#         with self.assertRaises(DataError):
#             self.input.process_verify_json(JSON__STR_BAD_DATA)
#
#
# OBJ_INCORRECT_HASH = {
#     "xeDkbtzK6Y8gXoXVde+XuKnJ3ICVbUtkFZFHZQeI2jDEls0cNTCuqDMg1LcEcNtRFoUx26+ZZlKG6UMquoNEUw==":
#     {
#         KEY_VALUE: 100,
#         KEY_FROM_ADDR: "a",
#         KEY_TO_ADDR: "b"
#     }
# }
# OBJ_BAD_KEY = {
#     "xeDkbtzK6Y8gXoXVde+XuKnJ3ICVbUtkFZFHZQeI2jDEls0cNTCuqDMg1LcEcNtRFoUx26+ZZlKG6UMquoNEUw==":
#     {
#         KEY_VALUE: 100,
#         'bad_key': "a",
#         KEY_TO_ADDR: "b"
#     }
# }
#
# JSON_STR = str(
#     '''{{"jX8Z/UvTi+GO6i8jN6/XVkHI1eFW3TZCj9r/ATmma1sJ5g7kA8legR0zj12zbJehcx1d4teE8QNTx+RBlEepnw==": '''
#     '''{{"{}": 100, "{}": "a", "{}": "b"}}}}'''.format(KEY_VALUE, KEY_FROM_ADDR, KEY_TO_ADDR))
#
# JSON__STR_BAD_DATA = str(
#     '''}}"jX8Z/UvTi+GO6i8jN6/XVkHI1eFW3TZCj9r/ATmma1sJ5g7kA8legR0zj12zbJehcx1d4teE8QNTx+RBlEepnw==": '''
#     '''{{"{}": 100, "{}": "a", "{}": "b"}}}}'''.format(KEY_VALUE, KEY_FROM_ADDR, KEY_TO_ADDR))

if __name__ == '__main__':
    unittest.main()
