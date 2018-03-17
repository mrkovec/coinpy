import logging
from typing import (
    Any, Dict, NewType
)

from .crypto import (
    Serializable, Hash, Pubkey, ID, Pubaddr, Utils
)
from . import JsonDict
from .errors import ValidationError, DataError

logger = logging.getLogger(__name__)

KEY_OUTPUT_AMOUNT = 'amount'
KEY_OUTPUT_PUBADDR = 'pubaddr'

OutputHash = Hash(digest_size = 33, person = b'OutputHash')

OutputID = NewType('OutputID', ID)

class Output(Serializable):
    def __init__(self, amount: float, pubaddr: Pubaddr) -> None:
        # logger.debug(f'Output.__init__({amount}, {pubaddr})')
        self.amount = amount
        self.pubaddr = pubaddr
        # self.__id = OutputID(ID(OutputHash.digest(str(self).encode('utf-8'))))

    def _serialize(self) -> JsonDict:
        return {
            KEY_OUTPUT_AMOUNT: self.amount,
            KEY_OUTPUT_PUBADDR: str(self.pubaddr)
        }

    def _unserialize(self, json_obj: JsonDict) -> None:
        try:
            self.amount = json_obj[KEY_OUTPUT_AMOUNT]
            self.pubaddr = Pubaddr(Utils.str_to_bytes(json_obj[KEY_OUTPUT_PUBADDR]))
        except Exception as e:
            raise DataError from e
        # self.__id = OutputID(ID(OutputHash.digest(str(self).encode('utf-8'))))

    def validate(self) -> None:
        if self.amount is None or self.pubaddr is None:
            raise ValidationError

    @property
    def id(self) -> OutputID:
        # return self.__id
        return OutputID(ID(OutputHash.digest(str(self).encode('utf-8'))))

# class CoinbaseInput(Output):
#     def validate(self) -> None:
#         # coinbase input must have empty pubaddr field
#         if self.amount is None or self.pubaddr is not None:
#             raise ValidationError
