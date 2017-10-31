import logging

from .crypto import (
    str_to_bytes, bytes_to_str, Serializable, Hash, Pubkey, ID, Pubaddr
)
    # import coinpy.core.errors #import DataError
from . import JsonDict, Any, Dict, NewType

# OutputID = NewType('OutputID', bytes)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# # create console handler and set level to debug
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# # create formatter
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# # add formatter to ch
# ch.setFormatter(formatter)
# # add ch to logger
# logger.addHandler(ch)


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
        self.amount = json_obj[KEY_OUTPUT_AMOUNT]
        self.pubaddr = Pubaddr(str_to_bytes(json_obj[KEY_OUTPUT_PUBADDR]))
        self.__id = OutputID(ID(OutputHash.digest(str(self).encode('utf-8'))))

    def __bool__(self) -> bool:
        return (self.amount is not None and self.pubaddr is not None)

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
