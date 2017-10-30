from .crypto import (
    str_to_bytes, bytes_to_str, Serializable, Hash, Pubkey, ID, Pubaddr
)
    # import coinpy.core.errors #import DataError
from . import JsonDict

KEY_OUTPUT_AMOUNT = 'amount'
KEY_OUTPUT_PUBADDR = 'pubaddr'
# KEY_OUTPUT_ID = 'outp_id'

class OutputHash(Hash, digest_size = 33, person = b'OutputHash'):
    pass

class OutputID(ID, id_hash = OutputHash):
    @classmethod
    def from_obj(cls, json_obj: JsonDict) -> 'OutputID':
        id_new = cls()
        id_new.unserialize(json_obj)
        return id_new
    #
    # def _serialize(self) -> JsonDict:
    #     return {KEY_OUTPUT_ID: str(self)}
    #
    # def _unserialize(self, json_obj: JsonDict) -> None:
    #     self = OutputID(str_to_bytes(json_obj[KEY_OUTPUT_ID]))


class Output(Serializable):
    __id: OutputID

    def __init__(self, amount: float  = None, pubaddr: Pubaddr = None) -> None:
        self.__id = OutputID()
        self.amount = amount
        self.pubaddr = pubaddr

    def serialize(self) -> JsonDict:
        return {KEY_OUTPUT_AMOUNT: self.amount, KEY_OUTPUT_PUBADDR: str(self.pubaddr)}

    def unserialize(self, json_obj: JsonDict) -> None:
        self.amount = json_obj[KEY_OUTPUT_AMOUNT]
        self.pubaddr = Pubaddr(str_to_bytes(json_obj[KEY_OUTPUT_PUBADDR]))

    @classmethod
    def from_obj(cls, json_obj: JsonDict) -> 'Output':
        outp_new = cls()
        outp_new.unserialize(json_obj)
        return outp_new

    @classmethod
    def from_json(cls, json_str: str) -> 'Output':
        outp_new = cls()
        outp_new.unserialize_json(json_str)
        return outp_new

    @property
    def id(self) -> OutputID:
        self.__id.digest(self.to_json().encode('utf-8'))
        return self.__id
