import hashlib
import base64
import json
import io
import logging

from ecdsa import ( # type: ignore
    SigningKey, VerifyingKey, SECP256k1
)
from .errors import (
    Error, SerializeError, ValidationError, DataError
)
from . import JsonDict, Tuple, Dict, TypeVar, Any, Type, Union, Optional

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class Utils(object):
    @staticmethod
    def str_to_bytes(data_str: Optional[str]) -> bytes:
        if data_str is None:
            raise DataError('no data to convert')
        return base64.b64decode(data_str)

    @staticmethod
    def bytes_to_str(data_bytes: Optional[bytes]) -> str:
        if data_bytes is None:
            raise DataError('no data to convert')
        return base64.b64encode(data_bytes).decode('utf-8')


class Hash(object):
    """A simple representation of a human being.

    :param name: A string, the person's name.
    :param age: An int, the person's age.
    """
    def __init__(self,  digest_size: int, person: bytes) -> None:
        self.__digest_size = digest_size
        self.__person = person

    # def __init_subclass__(cls,  digest_size: int, person: bytes) -> None:
    #     logger.debug(f'Hash__init_subclass__({digest_size},{person})')
    #     cls.__digest_size = digest_size
    #     cls.__person = person
    #     super().__init_subclass__()

    def digest(self, data: bytes) -> bytes:
        h = hashlib.blake2b(digest_size=self.__digest_size, person=self.__person) # type: ignore
        h.update(data)
        return h.digest()


SignatureHash = Hash(digest_size = 64, person = b'SignatureHash')
PubaddrHash = Hash(digest_size = 33, person = b'PubaddrHash')

T = TypeVar('T', bound='Serializable')

class Serializable(object):
    def _serialize(self) -> JsonDict:
        raise NotImplementedError('_serialize')

    def _unserialize(self, json_obj: JsonDict) -> None:
        raise NotImplementedError('_unserialize')

    # def __bool__(self) -> bool:
    #     raise NotImplementedError
    def validate(self) -> None:
        raise NotImplementedError('validate')

    def serialize(self) -> JsonDict:
        self.validate()
        return self._serialize()

    @classmethod
    def unserialize(cls: Type[T], json_obj: JsonDict) -> T:
        serial_new = cls.__new__(cls)
        serial_new._unserialize(json_obj)
        serial_new.validate()
        return serial_new

    @classmethod
    def unserialize_json(cls: Type[T], json_str: str) -> T:
        try:
            return cls.unserialize(json.loads(json_str))
        except Error:
            logger.exception('call failed')
            raise
        except Exception as e:
            raise SerializeError(str(e)) from e

    # @classmethod
    # def unserialize_json(cls, json_str: str) -> Any:
    #     try:
    #         return cls.unserialize(json.loads(json_str))
    #     except Error:
    #         raise
    #     except Exception as e:
    #         raise SerializeError('incorrect data', e)

    # def unserialize(self, json_obj: JsonDict) -> None:
    #     # logger.debug('Serializable unserialize')
    #     self._unserial(json_obj)
    #     if not self:
    #         raise ValidationError()
    #
    # def unserialize_json(self, json_str: str) -> None:
    #     try:
    #         self.unserialize(json.loads(json_str))
    #         # if not self:
    #         #     raise ValidationError()
    #     except Error:
    #         raise
    #     except Exception as e:
    #         raise SerializeError('incorrect data', e)

    def __str__(self) -> str:
        return SerializableEncoder().encode(self)


class SerializableEncoder(json.JSONEncoder):
    def default(self, obj: Serializable) -> Union[JsonDict, str]:
        try:
            # if not self:
            #     raise ValidationError()
            return obj.serialize()
        except Error:
            logger.exception('call failed')
            raise
        except NotImplementedError:
            return str(obj)
        except Exception as e:
            logger.exception('not serializable')
            raise SerializeError(str(e)) from e



class ID(Serializable):
    # __hash: Hash
    # __val: bytes

    def __init__(self, id_bytes: bytes) -> None:
        logger.debug(f'ID__init__({id_bytes})')
        # self.__val = self.__hash.digest(id_bytes)
        self.__val = id_bytes

    # def __init_subclass__(cls, id_hash: Hash) -> None:
    #     logger.debug(f'ID__init_subclass__({id_hash!r})')
    #     cls.__hash = id_hash()
    #     super().__init_subclass__()

    def __eq__(self, other: 'ID') -> bool: # type: ignore
        return self.__val == other.__val

    def __str__(self) -> str:
        # if self.__val is None:
        #     raise DataError('empty data')
        return Utils.bytes_to_str(self.__val)

    def __bytes__(self) -> bytes:
        # if self.__val is None:
        #     raise DataError('empty data')
        return self.__val

    # def __bool__(self) -> bool:
    #     if self.__val is None:
    #         return False
    #     return True

    # def digest(self, data_bytes: bytes) -> None:
    #     self.__val = self.__hash.digest(data_bytes)


    # def _serialize(self) -> JsonDict:
    #     # return {'id': bytes_to_str(self.__id)}
    #     return bytes_to_str(self.__id)
    #
    # def _unserialize(self, json_obj: JsonDict) -> None:
    #     # self.__id = str_to_bytes(json_obj['id'])
    #     self.__id = str_to_bytes(json_obj)



# class PubkeyHash(Hash, digest_size = 33, person = b'PubkeyHash'):
#     pass

# class Pubaddr(ID), id_hash=PubkeyHash):
class Pubaddr(ID):
    # __hash = PubkeyHash()
    @classmethod
    def from_pubkey(cls, pubkey: 'Pubkey') -> 'Pubaddr':
        return cls(PubaddrHash.digest(bytes(pubkey)))

class Pubkey(object):
    def __init__(self, vk_bytes: bytes) -> None:
        self.__verifying_key = VerifyingKey.from_string(vk_bytes, curve=SECP256k1)

    def __str__(self) -> str:
        return Utils.bytes_to_str(self.__verifying_key.to_string())

    def __bytes__(self) -> bytes:
        return self.__verifying_key.to_string()

    def verify(self, signature: bytes, message: bytes) -> bool:
        return self.__verifying_key.verify(signature, SignatureHash.digest(message))

    @property
    def pubaddr(self) -> Pubaddr:
        return Pubaddr.from_pubkey(self)




# class SignatureHash(Hash, digest_size = 64, person = b'SignatureHash'):
#     pass


class Privkey(object):
    def __init__(self, sk: SigningKey) -> None:
        self.__signing_key = sk

    @classmethod
    def from_pem(cls, pem_data: io.StringIO) -> 'Privkey':
        return cls(SigningKey.from_pem(pem_data.read()))


    def sign(self, message: bytes) -> Tuple[Pubkey, bytes]:
        return (self.pubkey, self.__signing_key.sign(SignatureHash.digest(message)))

    @property
    def pubkey(self) -> Pubkey:
        return Pubkey(self.__signing_key.get_verifying_key().to_string())
