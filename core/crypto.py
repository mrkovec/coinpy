from typing import Dict, Union
from hashlib import blake2b
from base64 import b64encode, b64decode
from json import JSONEncoder, loads
from .errors import Error, HashError, DataError

class Hash:
    def __init__(self, hash_bytes: bytes) -> None:
        self.__val = hash_bytes

    @classmethod
    def from_str(cls, hash_str: str) -> 'Hash':
        return cls(bytes(b64decode(hash_str)))

    def get_bytes(self) -> bytes:
        return self.__val

    def get_str(self) -> str:
        return b64encode(self.__val).decode()


def hash_from_str(text: str) -> Hash:
    return Hash(blake2b(text.encode('utf-8'), digest_size=64, fanout=2, depth=255, leaf_size=4096).digest())


def hash_from_obj(obj: object) -> Hash:
    return hash_from_str(CryptoEncoder().encode(obj))


class CryptoObj:
    def _prepare_data(self) -> object: # pragma: no cover
        pass

    def _set_data(self, id: Hash, data: object) -> None: # pragma: no cover
        pass

    def check_hash(self, hash: Hash) -> bool:
        return hash_from_obj(self._prepare_data()).get_bytes() == hash.get_bytes()

    def process_verify_obj(self, json_obj: object) -> None:
        try:
            for hash_str, data_obj in json_obj.items():
                obj_hash = Hash.from_str(hash_str)
                self._set_data(obj_hash, data_obj)
                if not self.check_hash(obj_hash):
                    raise HashError('incorrect hash', hash_str)
        except Error:
            raise
        except Exception as e:
            raise DataError('incorrect data', e)

    def process_verify_json(self, json_str: str) -> None:
        try:
            json_obj = loads(json_str)
        except Exception as e:
            raise DataError('json error', e)
        self.process_verify_obj(json_obj)

    def to_json(self) -> str:
        return CryptoEncoder().encode(self)


class CryptoEncoder(JSONEncoder):
    def default(self, obj):
        try:
            p = obj._prepare_data()
            p_hash = hash_from_str(self.encode(p))
            return {p_hash.get_str(): p}
        except:
            return json.JSONEncoder.default(self, obj)
