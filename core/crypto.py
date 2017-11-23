import hashlib
import base64
import json
import io
import os
import logging

from ecdsa import (
    SigningKey, VerifyingKey, SECP256k1
)
from .errors import (
    Error, SerializeError, ValidationError, DataError
)
from . import (
    JsonDict, Tuple, Dict, TypeVar, Any, Type, Union, Optional
)
from coinpy.definitions import KEYS_PATH
# logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class Utils(object):
    @staticmethod
    def str_to_bytes(data_str: Optional[str]) -> bytes:
        if data_str is None:
            raise ValueError('no data to convert')
        return base64.b64decode(data_str)

    @staticmethod
    def bytes_to_str(data_bytes: Optional[bytes]) -> str:
        if data_bytes is None:
            raise ValueError('no data to convert')
        return base64.b64encode(data_bytes).decode('utf-8')


class Hash(object):
    def __init__(self,  digest_size: int, person: bytes) -> None:
        self.__digest_size = digest_size
        self.__person = person

    def digest(self, data: bytes) -> bytes:
        h = hashlib.blake2b(digest_size=self.__digest_size, person=self.__person) # type: ignore
        h.update(data)
        return h.digest()


T = TypeVar('T', bound='Serializable')

class Serializable(object):
    def _serialize(self) -> JsonDict:
        raise NotImplementedError('_serialize')

    def _unserialize(self, json_obj: JsonDict) -> None:
        raise NotImplementedError('_unserialize')

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

    def __str__(self) -> str:
        return SerializableEncoder().encode(self)


class SerializableEncoder(json.JSONEncoder):
    def default(self, obj: Serializable) -> Union[JsonDict, str]:
        try:
            return obj.serialize()
        except Error:
            raise
        except NotImplementedError:
            return str(obj)
        except Exception as e:
            raise SerializeError(str(e)) from e


class ID(Serializable):
    def __init__(self, id_bytes: bytes) -> None:
        # logger.debug(f'ID__init__({id_bytes})')
        self.__val = id_bytes

    def __eq__(self, other: 'ID') -> bool: # type: ignore
        return self.__val == other.__val

    def __str__(self) -> str:
        return Utils.bytes_to_str(self.__val)

    def __bytes__(self) -> bytes:
        return self.__val

    def __hash__(self) -> int:
        return self.__val.__hash__()


SignatureHash = Hash(digest_size = 64, person = b'SignatureHash')
PubaddrHash = Hash(digest_size = 33, person = b'PubaddrHash')


class Pubaddr(ID):
    @classmethod
    def from_pubkey(cls, pubkey: 'Pubkey') -> 'Pubaddr':
        return cls(PubaddrHash.digest(bytes(pubkey)))


class Pubkey(object):
    def __init__(self, vk_bytes: bytes) -> None:
        self.__verifying_key = VerifyingKey.from_string(vk_bytes, curve=SECP256k1)

    # @classmethod
    # def from_str(cls, vk_str: str) -> 'Pubkey':
    #     return cls(Utils.str_to_bytes(vk_str))

    def __str__(self) -> str:
        return Utils.bytes_to_str(self.__verifying_key.to_string())

    def __bytes__(self) -> bytes:
        return self.__verifying_key.to_string()

    def verify(self, signature: bytes, message: bytes) -> bool:
        return self.__verifying_key.verify(signature, SignatureHash.digest(message))

    @property
    def pubaddr(self) -> Pubaddr:
        return Pubaddr.from_pubkey(self)


class Privkey(object):
    def __init__(self, sk: SigningKey) -> None:
        self.__signing_key = sk

    @classmethod
    def new(cls) -> 'Privkey':
        return cls(SigningKey.generate(curve=SECP256k1))

    @classmethod
    def from_pem(cls, pem_data: io.BufferedIOBase) -> 'Privkey':
        return cls(SigningKey.from_pem(pem_data.read()))

    def to_pem(self) -> str:
        return self.__signing_key.to_pem()

    def sign(self, message: bytes) -> Tuple[Pubkey, bytes]:
        return (self.pubkey, self.__signing_key.sign(SignatureHash.digest(message)))

    @property
    def pubkey(self) -> Pubkey:
        return Pubkey(self.__signing_key.get_verifying_key().to_string())


class PrivkeyStorage(object):
    @staticmethod
    def load_signing_keys() -> Dict[str, Privkey]:
        if not os.path.exists(KEYS_PATH):
            os.makedirs(KEYS_PATH)
        signing_keys = {}
        for root, _, files in os.walk(KEYS_PATH):
            for fn in files:
                if fn.endswith('.pem'):
                    with open(os.path.join(root, fn), 'rb') as f:
                        sk = Privkey.from_pem(f)
                        signing_keys[fn[:-4]] = sk
        if len(signing_keys) == 0:
            # default privkey
            sk = Privkey.new()
            signing_keys['default'] = sk
            PrivkeyStorage.store_signing_key('default', sk)
        return signing_keys

    @staticmethod
    def store_signing_key(name: str, privkey: Privkey) -> None:
        f_n = os.path.join(KEYS_PATH, f'{name}.pem')
        if os.path.isfile(f_n):
            raise Error(f'privkey {name} already exisis')
        with open(f_n, 'wb') as f:
            f.write(privkey.to_pem())
