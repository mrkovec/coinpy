import logging
# from json import loads as JSONloads

from .output import (
    Output, OutputID
)
from .crypto import (
    Hash, Serializable, ID, Pubkey, Privkey, SerializableEncoder, Utils
)
from .errors import DataError, ValidationError

from . import List, JsonDict, Optional, NewType

TRANS_VERSION = 1

KEY_TRANS_VERSION = 'ver'
KEY_TRANS_TIME_STAMP = 'time_stamp'
KEY_TRANS_INPS = 'inps'
KEY_TRANS_OUTPS = 'outps'
KEY_TRANS_SIGN = 'sign'
KEY_TRANS_SIGN_PUBKEY = 'pubkey'

logger = logging.getLogger(__name__)

TransHash = Hash(digest_size = 33, person = b'TransHash')
TransID = NewType('TransID', ID)

class Trans(Serializable):
    def __init__(self, time_stamp: float, inps: List[OutputID], outps: List[Output]) -> None:
        self.version = TRANS_VERSION
        self.time_stamp = time_stamp
        self.inps = inps
        self.outps = outps
        self.signature: Optional[bytes] = None
        self.signature_pubkey: Optional[Pubkey] = None
        # self.__id: Optional[TransID] = None


    def __sign_data(self) -> bytes:
        data = {
            KEY_TRANS_VERSION: self.version,
            KEY_TRANS_TIME_STAMP: self.time_stamp,
            KEY_TRANS_INPS: self.inps,
            KEY_TRANS_OUTPS: self.outps,
        }
        return SerializableEncoder().encode(data).encode('utf-8')

    def sign(self, signing_key: Privkey) -> None:
        self.signature_pubkey, self.signature = signing_key.sign(self.__sign_data())
        # self.__id = TransID(ID(TransHash.digest(str(self).encode('utf-8'))))

    def verify_sign(self) -> None:
        if self.signature_pubkey is None or self.signature is None:
            raise ValidationError
        if not self.signature_pubkey.verify(self.signature, self.__sign_data()):
            raise ValidationError

    def _serialize(self) -> JsonDict:
        return {
            KEY_TRANS_VERSION: self.version,
            KEY_TRANS_TIME_STAMP: self.time_stamp,
            KEY_TRANS_INPS: self.inps,
            KEY_TRANS_OUTPS: self.outps,
            KEY_TRANS_SIGN : Utils.bytes_to_str(self.signature),
            KEY_TRANS_SIGN_PUBKEY : str(self.signature_pubkey)
        }

    def validate(self) -> None:
        if (self.time_stamp is None or self.inps is None or self.outps is None
                or self.signature is None or self.signature_pubkey is None
                or len(self.inps) == 0 or len(self.outps) == 0):
            raise ValidationError


    def _unserialize(self, json_obj: JsonDict) -> None:
        try:
            self.version = json_obj[KEY_TRANS_VERSION]
            self.time_stamp = json_obj[KEY_TRANS_TIME_STAMP]
            self.inps = []
            for inp in json_obj[KEY_TRANS_INPS]:
                self.inps.append(OutputID(ID(Utils.str_to_bytes(inp))))
            self.outps = []
            for outp in json_obj[KEY_TRANS_OUTPS]:
                self.outps.append(Output.unserialize(outp))
            self.signature = Utils.str_to_bytes(json_obj[KEY_TRANS_SIGN])
            self.signature_pubkey = Pubkey(Utils.str_to_bytes(json_obj[KEY_TRANS_SIGN_PUBKEY]))
        except Exception as e:
            raise DataError(str(e)) from e
        # self.__id = TransID(ID(TransHash.digest(str(self).encode('utf-8'))))

    @property
    def id(self) -> TransID:
        # if self.__id is None:
        #     raise ValidationError
        # return self.__id
        return TransID(ID(TransHash.digest(str(self).encode('utf-8'))))


class CoinbaseTrans(Trans):
    # pass
    def validate(self) -> None:
        if (self.time_stamp is None or self.inps is None or self.outps is None
                or self.signature is None or self.signature_pubkey is None
                or len(self.outps) == 0):
            raise ValidationError
