import hashlib
import base64
import json
import io

from ecdsa import (
    SigningKey, VerifyingKey, SECP256k1
)
from .errors import (
    Error, DataError
)
from . import JsonDict, Tuple

class SerializeError(Error):
    pass
class ValidationError(Error):
    pass

def str_to_bytes(data_str: str) -> bytes:
    return base64.b64decode(data_str)

def bytes_to_str(data_bytes: bytes) -> str:
    return base64.b64encode(data_bytes).decode('utf-8')

class Hash(object):
    """A simple representation of a human being.

    :param name: A string, the person's name.
    :param age: An int, the person's age.
    """
    def __init_subclass__(cls,  digest_size: int, person: bytes) -> None:
        cls.__digest_size = digest_size
        cls.__person = person
        super().__init_subclass__()

    def digest(self, data: bytes) -> bytes:
        h = hashlib.blake2b(digest_size=self.__digest_size, person=self.__person)
        h.update(data)
        return h.digest()






class Serializable(object):
    # __hash: Hash
    # _id: ID

    # def __init_subclass__(cls, object_hash: Hash) -> None:
    #     cls.__hash = object_hash
    #     super().__init_subclass__()

    def serialize(self) -> JsonDict:
        raise Error('_serialize not implemented')

    def unserialize(self, json_obj: JsonDict) -> None:
        raise Error('_unserialize not implemented')

    def __bool__(self) -> bool:
        return True

    # def _id_generate(self) -> None:
    #     self._id = ID(self.__hash.digest(self.to_json().encode('utf-8')))

    # def unserialize(self, json_obj: JsonDict) -> None:
    #     self._unserialize(json_obj)
        # self._id_generate()

    def unserialize_json(self, json_str: str) -> None:
        try:
            # def dec(dct) -> dict:
            #     print('..............')
            #     print(dct)
            #
            # JSONDecoder(object_hook=dec).decode(json_str)
            self.unserialize(json.loads(json_str))
            if not self:
                raise ValidationError()
        except Error:
            raise
        except Exception as e:
            raise SerializeError('incorrect data', e)

    def to_json(self) -> str:
        return SerializableEncoder().encode(self)


class SerializableEncoder(json.JSONEncoder):
    def default(self, obj: Serializable) -> JsonDict:
        try:
            if not self:
                raise ValidationError()
            return obj.serialize()
        except Error:
            raise
        except Exception as e:
            # raise DataError('not serializable', e)
            return json.JSONEncoder.default(self, obj)


class ID(Serializable):
    # __hash: Hash
    # __val: bytes

    def __init__(self, id_bytes: bytes = None) -> None:
        self.__val = id_bytes

    def __init_subclass__(cls, id_hash: Hash) -> None:
        cls.__hash = id_hash()
        super().__init_subclass__()

    def __eq__(self, other: 'ID') -> bool: # type: ignore
        # print("A __eq__ called: %r == %r ?" % (self, other))
        # if not self or not other:
        #     raise DataError('empty data')
        return self.__val == other.__val

    def __str__(self) -> str:
        if self.__val is None:
            raise DataError('empty data')
        return bytes_to_str(self.__val)

    def __bytes__(self) -> bytes:
        if self.__val is None:
            raise DataError('empty data')
        return self.__val

    def __bool__(self) -> bool:
        if self.__val is None:
            return False
        return True

    # def serialize(self) -> JsonDict:
    #     if self.__val is None:
    #         raise DataError('empty data')
    #     return {'id': bytes_to_str(self.__val)}
    #
    # def unserialize(self, json_obj: JsonDict) -> None:
    #      self.__val = str_to_bytes(json_obj['id'])
    # @property
    # def id_bytes(self) -> bytes:
    #     return self.__val
    #
    # @property
    # def id_str(self) -> str:
    #     return bytes_to_str(self.__val)

    def digest(self, data_bytes: bytes) -> None:
        self.__val = self.__hash.digest(data_bytes)


    # def _serialize(self) -> JsonDict:
    #     # return {'id': bytes_to_str(self.__id)}
    #     return bytes_to_str(self.__id)
    #
    # def _unserialize(self, json_obj: JsonDict) -> None:
    #     # self.__id = str_to_bytes(json_obj['id'])
    #     self.__id = str_to_bytes(json_obj)


class PubkeyHash(Hash, digest_size = 33, person = b'PubkeyHash'):
    pass

class Pubaddr(ID, id_hash=PubkeyHash):
    @classmethod
    def from_pubkey(cls, pubkey: 'Pubkey') -> 'Pubaddr':
        return cls(PubkeyHash().digest(bytes(pubkey)))


class Pubkey(object):
    def __init__(self, vk_bytes: bytes) -> None:
        self.__verifying_key = VerifyingKey.from_string(vk_bytes, curve=SECP256k1)

    def __str__(self) -> str:
        return bytes_to_str(self.__verifying_key.to_string())

    def __bytes__(self) -> bytes:
        return self.__verifying_key.to_string()

    def verify(self, signature: bytes, message: bytes) -> bool:
        return self.__verifying_key.verify(signature, message)

    @property
    def pubaddr(self) -> Pubaddr:
        return Pubaddr.from_pubkey(self)


class SignatureHash(Hash, digest_size = 64, person = b'SignatureHash'):
    pass

# class Signature(Serializable):
#     __hash: SignatureHash
#     __sign: bytes
#     __pubkey: Pubkey
#     @classmethod
#     def generate(cls, data: bytes, signing_key: 'Privkey'):
#         sig_new = cls()
#         sig_new.__hash = SignatureHash()
#         sig_new.__sign = signing_key.sign(self.digest(data))
#         sig_new.__pubkey = signing_key.get_verifying_key().to_string()
#
#     def serialize(self) -> JsonDict:
#         return {'sig': bytes_to_str(__sign), 'pubkey': str(self.__pubkey)}
#
#     def unserialize(self, json_obj: JsonDict) -> None:
#         self.amount = json_obj[KEY_OUTPUT_AMOUNT]
#         self.pubaddr = Pubaddr(str_to_bytes(json_obj[KEY_OUTPUT_PUBADDR]))


class Privkey(object):
    def __init__(self, sk: SigningKey) -> None:
        self.__signing_key = sk

    @classmethod
    def from_pem(cls, pem_data: io.StringIO) -> 'Privkey':
        return cls(SigningKey.from_pem(pem_data.read()))


    def sign(self, message: bytes) -> Tuple[Pubkey, bytes]:
        return (self.pubkey, self.__signing_key.sign(SignatureHash().digest(message)))

    @property
    def pubkey(self) -> Pubkey:
        return Pubkey(self.__signing_key.get_verifying_key().to_string())
