"""Transaction functionality."""
import logging

from time import time

from .output import (
    Output, OutputID
)
from .crypto import (
    Hash, Serializable, ID, Pubkey, Privkey, SerializableEncoder, Utils as CryptoUtils, Pubaddr, PrivkeyStorage
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

COINBASE_INP_ID = OutputID(ID(b'cinpt'))

logger = logging.getLogger(__name__)

TransactionHash = Hash(digest_size = 33, person = b'TransactionHash')
TransactionID = NewType('TransactionID', ID)

class Transaction(Serializable):
    def __init__(self, time_stamp: float, inps: List[OutputID], outps: List[Output]) -> None:
        self.version = TRANS_VERSION
        self.time_stamp = time_stamp
        self.inputs = inps
        self.outputs = outps
        self.signature: Optional[bytes] = None
        self.signature_pubkey: Optional[Pubkey] = None

    def __sign_data(self) -> bytes:
        data = {
            KEY_TRANS_VERSION: self.version,
            KEY_TRANS_TIME_STAMP: self.time_stamp,
            KEY_TRANS_INPS: self.inputs,
            KEY_TRANS_OUTPS: self.outputs,
        }
        return SerializableEncoder().encode(data).encode('utf-8')

    def sign(self, signing_key: Privkey) -> None:
        self.signature_pubkey, self.signature = signing_key.sign(self.__sign_data())

    def verify_sign(self) -> None:
        if self.signature_pubkey is None or self.signature is None:
            raise ValidationError
        if not self.signature_pubkey.verify(self.signature, self.__sign_data()):
            raise ValidationError

    def _serialize(self) -> JsonDict:
        return {
            KEY_TRANS_VERSION: self.version,
            KEY_TRANS_TIME_STAMP: self.time_stamp,
            KEY_TRANS_INPS: self.inputs,
            KEY_TRANS_OUTPS: self.outputs,
            KEY_TRANS_SIGN : CryptoUtils.bytes_to_str(self.signature),
            KEY_TRANS_SIGN_PUBKEY : str(self.signature_pubkey)
        }

    def validate(self) -> None:
        if (self.time_stamp is None or self.inputs is None or self.outputs is None
                or self.signature is None or self.signature_pubkey is None
                or len(self.inputs) == 0 or len(self.outputs) == 0):
            raise ValidationError

    def _unserialize(self, json_obj: JsonDict) -> None:
        try:
            self.version = json_obj[KEY_TRANS_VERSION]
            self.time_stamp = json_obj[KEY_TRANS_TIME_STAMP]
            self.inputs = []
            for inp in json_obj[KEY_TRANS_INPS]:
                self.inputs.append(OutputID(ID(CryptoUtils.str_to_bytes(inp))))
            self.outputs = []
            for outp in json_obj[KEY_TRANS_OUTPS]:
                self.outputs.append(Output.unserialize(outp))
            self.signature = CryptoUtils.str_to_bytes(json_obj[KEY_TRANS_SIGN])
            self.signature_pubkey = Pubkey(CryptoUtils.str_to_bytes(json_obj[KEY_TRANS_SIGN_PUBKEY]))
        except Exception as e:
            raise DataError(str(e)) from e

    @property
    def id(self) -> TransactionID:
        return TransactionID(ID(TransactionHash.digest(str(self).encode('utf-8'))))


class Utils(object):
    @staticmethod
    def coinbase_transaction() -> Transaction:
        coinbase_inpt_id = COINBASE_INP_ID
        coinbase_outp = Output(10, Pubaddr(b''))
        coinbase = Transaction(time(), [coinbase_inpt_id], [coinbase_outp])
        # sign coinbase trx with default privkey
        sk = PrivkeyStorage.load_signing_keys()
        coinbase.sign(sk['default'])
        return coinbase

    @staticmethod
    def transaction_is_coinbase(trx: Transaction) -> bool:
        if len(trx.inputs) == 1 and len(trx.outputs) == 1 and trx.inputs[0] == COINBASE_INP_ID:
            return True
        return False

# class CoinbaseTransaction(Transaction):
#     def __init__(self, time_stamp: float, inps: List[OutputID], outps: List[Output]) -> None:

    # def validate(self) -> None:
    #     if (self.time_stamp is None or self.inputs is None or self.outputs is None
    #             or len(self.outputs) == 0):
    #         raise ValidationError
