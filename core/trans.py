# import time
# from json import loads as JSONloads

from .output import (
    Output, OutputID
)
from .crypto import (
    Hash, Serializable, ID, Pubkey, Privkey, SerializableEncoder, bytes_to_str, str_to_bytes
)
from .errors import DataError

from . import List, JsonDict, Optional, NewType

KEY_TRANS_TIME_STAMP = 'time_stamp'
KEY_TRANS_INPS = 'inps'
KEY_TRANS_OUTPS = 'outps'
KEY_TRANS_SIGN = 'sign'
KEY_TRANS_SIGN_PUBKEY = 'pubkey'


TransHash = Hash(digest_size = 33, person = b'TransHash')
# class TransHash(Hash, digest_size = 33, person = b'TransHash'):
#     pass

TransID = NewType('TransID', ID)
# class TransID(ID, id_hash = TransHash):
#     pass
    # @classmethod
    # def from_obj(cls, json_obj: JsonDict) -> 'TransID':
    #     trx_new = cls()
    #     trx_new.unserialize(json_obj)
    #     return trx_new


class Trans(Serializable):
    # __id: TransID

    def __init__(self, time_stamp: float, inps: List[OutputID], outps: List[Output]) -> None:
        # self.__id = TransID()
        # if time_stamp is None:
        #     self.time_stamp = time.time()
        # else:
        # self.__privkey = signing_key
        self.time_stamp = time_stamp
        self.inps = inps
        self.outps = outps
        self.signature: Optional[bytes] = None
        self.signature_pubkey: Optional[Pubkey] = None

        # if signing_key is not None:
        #     self.sign(signing_key)


    def sign(self, signing_key: Privkey) -> None:
        data = {
            KEY_TRANS_TIME_STAMP: self.time_stamp,
            KEY_TRANS_INPS: self.inps,
            KEY_TRANS_OUTPS: self.outps,
        }
        self.signature_pubkey, self.signature = signing_key.sign(SerializableEncoder().encode(data).encode('utf-8'))
        self.__id = TransID(ID(TransHash.digest(str(self).encode('utf-8'))))


    def _serialize(self) -> JsonDict:
        # self.validate()
        return {
            KEY_TRANS_TIME_STAMP: self.time_stamp,
            KEY_TRANS_INPS: self.inps,
            KEY_TRANS_OUTPS: self.outps,
            KEY_TRANS_SIGN : bytes_to_str(self.signature),
            KEY_TRANS_SIGN_PUBKEY : str(self.signature_pubkey)
        }

    def __bool__(self) -> bool:
        return (self.time_stamp is not None and self.inps is not None and self.outps is not None
            and self.signature is not None and self.signature_pubkey is not None)

    def _unserialize(self, json_obj: JsonDict) -> None:
        self.time_stamp = json_obj[KEY_TRANS_TIME_STAMP]
        self.inps = []
        for inp in json_obj[KEY_TRANS_INPS]:
            self.inps.append(OutputID(ID(str_to_bytes(inp))))
        self.outps = []
        for outp in json_obj[KEY_TRANS_OUTPS]:
            self.outps.append(Output.unserialize(outp))
        self.signature = str_to_bytes(json_obj[KEY_TRANS_SIGN])
        self.signature_pubkey = Pubkey(str_to_bytes(json_obj[KEY_TRANS_SIGN_PUBKEY]))
        self.__id = TransID(ID(TransHash.digest(str(self).encode('utf-8'))))
        # self.validate()

    # @classmethod
    # def from_json(cls, json_str: str) -> 'Trans':
    #     new_outp = cls()
    #     new_outp.unserialize_json(json_str)
    #     return new_outp

    @property
    def id(self) -> TransID:
        # self.__id.digest(self.to_json().encode('utf-8'))
        return self.__id

    # def add_inp(self, inp: OutputID) -> None:
    #     self.inps.append(inp)
    #
    # def add_outp(self, outp: Output) -> None:
    #     self.outps.append(outp)

    # def sign(self, privkey: Privkey) -> None:
    #     pass
