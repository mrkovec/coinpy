import logging

from .crypto import (
    Serializable, Hash, Pubkey, ID, Pubaddr, Utils
)
    # import coinpy.core.errors #import DataError
from . import JsonDict, Any, Dict, NewType
from .errors import ValidationError, DataError

logger = logging.getLogger(__name__)

KEY_OUTPUT_AMOUNT = 'amount'
KEY_OUTPUT_PUBADDR = 'pubaddr'
# KEY_OUTPUT_ID = 'outp_id'

OutputHash = Hash(digest_size = 33, person = b'OutputHash')
# class OutputHash(Hash, digest_size = 33, person = b'OutputHash'):
#     pass

OutputID = NewType('OutputID', ID)
# class OutputID(ID, id_hash = OutputHash):
#     pass
    # @classmethod
    # def from_obj(cls, json_obj: JsonDict) -> 'OutputID':
    #     id_new = cls()
    #     id_new.unserialize(json_obj)
    #     return id_new
    #
    # def _serialize(self) -> JsonDict:
    #     return {KEY_OUTPUT_ID: str(self)}
    #
    # def _unserialize(self, json_obj: JsonDict) -> None:
    #     self = OutputID(str_to_bytes(json_obj[KEY_OUTPUT_ID]))


class Output(Serializable):
    # __hash = OutputHash()
    # __id: OutputID
    # def __init__(self) -> None:
    #     self.__id = OutputID()
    def __init__(self, amount: float, pubaddr: Pubaddr) -> None:
        logger.debug(f'Output.__init__({amount}, {pubaddr})')
        self.amount = amount
        self.pubaddr = pubaddr
        self.__id = OutputID(ID(OutputHash.digest(str(self).encode('utf-8'))))

    def _serialize(self) -> JsonDict:
        return {
            KEY_OUTPUT_AMOUNT: self.amount,
            KEY_OUTPUT_PUBADDR: str(self.pubaddr)
        }

    # @staticmethod
    # def _unserial(json_obj: JsonDict) -> Dict[str, Any]:
        # return {'amount': json_obj[KEY_OUTPUT_AMOUNT], 'pubaddr': Pubaddr(str_to_bytes(json_obj[KEY_OUTPUT_PUBADDR]))}

    def _unserialize(self, json_obj: JsonDict) -> None:
        try:
            self.amount = json_obj[KEY_OUTPUT_AMOUNT]
            self.pubaddr = Pubaddr(Utils.str_to_bytes(json_obj[KEY_OUTPUT_PUBADDR]))
        except Exception as e:
            raise DataError from e
        self.__id = OutputID(ID(OutputHash.digest(str(self).encode('utf-8'))))

    # def __bool__(self) -> bool:
    #     return (self.amount is not None and self.pubaddr is not None)

    def validate(self) -> None:
        if self.amount is None or self.pubaddr is None:
            raise ValidationError
    # @classmethod
    # def from_obj(cls, json_obj: JsonDict) -> 'Output':
    #     outp_new = cls()
    #     outp_new.unserialize(json_obj)
    #     return outp_new
    #
    # @classmethod
    # def from_json(cls, json_str: str) -> 'Output':
    #     outp_new = cls()
    #     outp_new.unserialize_json(json_str)
    #     return outp_new

    @property
    def id(self) -> OutputID:
        # self.__id.digest(self.to_json().encode('utf-8'))
        return self.__id

    # @classmethod
    # def _unserial(cls, json_obj: JsonDict) -> Any:
    #     return cls(json_obj[KEY_OUTPUT_AMOUNT], Pubaddr(str_to_bytes(json_obj[KEY_OUTPUT_PUBADDR])))
