# import time
# from json import loads as JSONloads

from .output import (
    Output, OutputID
)
from .crypto import (
    Hash, Serializable, ID, Pubkey, Privkey, SerializableEncoder, bytes_to_str, str_to_bytes
)
from .errors import DataError

from . import List, JsonDict, Optional

KEY_TRANS_TIME_STAMP = 'time_stamp'
KEY_TRANS_INPS = 'inps'
KEY_TRANS_OUTPS = 'outps'
KEY_TRANS_SIGN = 'sign'
KEY_TRANS_SIGN_PUBKEY = 'pubkey'


class TransHash(Hash, digest_size = 33, person = b'TransHash'):
    pass


class TransID(ID, id_hash = TransHash):
    @classmethod
    def from_obj(cls, json_obj: JsonDict) -> 'TransID':
        trx_new = cls()
        trx_new.unserialize(json_obj)
        return trx_new


class Trans(Serializable):
    # __id: TransID

    def __init__(self, time_stamp: float = None, inps: List[OutputID] = None, outps: List[Output] = None) -> None:
        self.__id = TransID()
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


    def serialize(self) -> JsonDict:
        # self.validate()
        return {
            KEY_TRANS_TIME_STAMP: self.time_stamp,
            KEY_TRANS_INPS: self.inps,
            KEY_TRANS_OUTPS: self.outps,
            KEY_TRANS_SIGN : bytes_to_str(self.signature),
            KEY_TRANS_SIGN_PUBKEY : str(self.signature_pubkey)
        }

    def validate(self) -> None:
        if self.time_stamp is None or self.inps is None or self.outps is None or self.signature is None or self.signature_pubkey is None:
            raise DataError('uncomplete data')

    def unserialize(self, json_obj: JsonDict) -> None:
        self.time_stamp = json_obj[KEY_TRANS_TIME_STAMP]
        for inp in json_obj[KEY_TRANS_INPS]:
            if self.inps is None:
                self.inps = []
            self.inps.append(OutputID.from_obj(inp))
        for outp in json_obj[KEY_TRANS_OUTPS]:
            if self.outps is None:
                self.outps = []
            self.outps.append(Output.from_obj(outp))
        self.signature = str_to_bytes(json_obj[KEY_TRANS_SIGN])
        self.signature_pubkey = Pubkey(str_to_bytes(json_obj[KEY_TRANS_SIGN_PUBKEY]))
        # self.validate()

    @classmethod
    def from_json(cls, json_str: str) -> 'Trans':
        new_outp = cls()
        new_outp.unserialize_json(json_str)
        return new_outp

    @property
    def id(self) -> TransID:
        self.__id.digest(self.to_json().encode('utf-8'))
        return self.__id

    # def add_inp(self, inp: OutputID) -> None:
    #     self.inps.append(inp)
    #
    # def add_outp(self, outp: Output) -> None:
    #     self.outps.append(outp)

    # def sign(self, privkey: Privkey) -> None:
    #     pass
