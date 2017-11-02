import unittest
import io

from .setup import *

from coinpy.core.crypto import (
    Serializable, Privkey, Pubkey, Utils, ID
)
from coinpy.core import JsonDict

class TestUtils(unittest.TestCase):
    def test_convert(self) -> None:
        self.assertEqual(b'abc', Utils.str_to_bytes(Utils.bytes_to_str(b'abc')))

    def test_convert_none(self) -> None:
        with self.assertRaises(ValueError):
            Utils.str_to_bytes(None)
        with self.assertRaises(ValueError):
            Utils.bytes_to_str(None)


class TestSerializable(unittest.TestCase):
    def setUp(self) -> None:
        self.obj = Obj(1)

    def test_serialize(self) -> None:
        self.assertEqual(1, Obj.unserialize(self.obj.serialize()).val)
        self.assertEqual(1, Obj.unserialize_json(str(self.obj)).val)

class TestID(unittest.TestCase):
    def test_id_data(self) -> None:
        id1 = ID(b'1')
        id2 = ID(bytes(id1))
        id3 = ID(Utils.str_to_bytes(str(id2)))
        self.assertTrue(id1 == id2 and id2 == id3 and id1 == id3)


class Obj(Serializable):
    def __init__(self, val:int = None) -> None:
        self.val = val
    def _serialize(self) -> JsonDict:
        return {'val': self.val}
    def _unserialize(self, json_obj: JsonDict) -> None:
        self.val = json_obj['val']
    def validate(self) -> None:
        if self.val is None:
            raise ValueError


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



if __name__ == '__main__':
    unittest.main()
