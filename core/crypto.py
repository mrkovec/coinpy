from hashlib import blake2b
from base64 import b64encode, b64decode
from json import JSONEncoder, loads
from typing import Dict, Any, Optional
JsonDict = Dict[str, Any]

from .errors import Error, HashError, DataError

class Hash(object):
    def __init__(self, hash_bytes: bytes) -> None:
        self.__val = hash_bytes

    @classmethod
    def from_str(cls, hash_str: str) -> 'Hash':
        return cls(bytes(b64decode(hash_str)))

    @classmethod
    def from_json(cls, json_str: str) -> 'Hash':
        return cls(blake2b(json_str.encode('utf-8'), digest_size=64, fanout=2, depth=255, leaf_size=4096).digest())

    @property
    def bytes_(self) -> bytes:
        return self.__val

    @property
    def str_(self) -> str:
        return b64encode(self.__val).decode()


class SerializableObject(object):
    _id: Optional[Hash] = None

    def _serialize(self) -> JsonDict:
        raise DataError('_serialize not implemented')

    def _unserialize(self, json_obj: JsonDict) -> None:
        raise DataError('_unserialize not implemented')

    def verify_hash(self, hash: Hash) -> bool:
        return Hash.from_json(SerializableObjectEncoder().encode(self._serialize())).bytes_ == hash.bytes_

    def verify_and_unserialize(self, json_obj: JsonDict) -> None:
        try:
            for hash_str, obj in json_obj.items():
                obj_hash = Hash.from_str(hash_str)
                self._unserialize(obj)
                self.id = obj_hash
                if not self.verify_hash(obj_hash):
                    raise HashError('incorrect hash')
        except Error:
            raise
        except Exception as e:
            raise DataError('incorrect data', e)

    def to_json(self) -> str:
        return SerializableObjectEncoder().encode(self)


class SerializableObjectEncoder(JSONEncoder):
    def default(self, obj: SerializableObject) -> JsonDict:
        try:
            p = obj._serialize()
            p_hash = Hash.from_json(self.encode(p))
            return {p_hash.str_: p}
        except Error:
            raise
        except Exception as e:
            raise HashError('not hashable', e)

# def hash_from_str(text: str) -> Hash:
#     return Hash(blake2b(text.encode('utf-8'), digest_size=64, fanout=2, depth=255, leaf_size=4096).digest())
#
#
# def hash_from_obj(obj: object) -> Hash:
#     return hash_from_str(HashedObjEncoder().encode(obj))


# class HashedObj:
#     # def _prepare_data(self) -> object: # pragma: no cover
#     #     pass
#     #
#     # def _set_data(self, id: Hash, data: object) -> None: # pragma: no cover
#     #     pass
#
#     def check_hash(self, hash: Hash) -> bool:
#         return hash_from_obj(self._prepare_data()).get_bytes() == hash.get_bytes()
#
#     def process_verify_obj(self, json_obj: object) -> None:
#         try:
#             for hash_str, data_obj in json_obj.items():
#                 obj_hash = Hash.from_str(hash_str)
#                 self._set_data(obj_hash, data_obj)
#                 if not self.check_hash(obj_hash):
#                     raise HashError('incorrect hash', hash_str)
#         except Error:
#             raise
#         except Exception as e:
#             raise DataError('incorrect data', e)
#
#     def process_verify_json(self, json_str: str) -> None:
#         try:
#             json_obj = loads(json_str)
#         except Exception as e:
#             raise DataError('json error', e)
#         self.process_verify_obj(json_obj)
#
#     def to_json(self) -> str:
#         return HashedObjEncoder().encode(self)
