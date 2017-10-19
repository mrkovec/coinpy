from typing import Dict, Any, Optional
JsonDict = Dict[str, Any]

from .crypto import SerializableObject, Hash

KEY_VALUE = 'val'
KEY_FROM_ADDR = 'from'
KEY_TO_ADDR = 'to'

class IOput(SerializableObject):
    def __init__(self, init_val: float, init_from: str, init_to: str) -> None:
        self._id: Optional[Hash] = None
        self.value = init_val
        self.from_addr = init_from
        self.to_addr = init_to

    @classmethod
    def from_obj(cls, json_obj: JsonDict) -> 'IOput':
        new_ioput = cls(-1,'','')
        new_ioput.verify_and_unserialize(json_obj)
        return new_ioput

    # @classmethod
    # def from_json_str(cls, json_str: str) -> 'IOput':
    #     new_ioput = cls(-1,'','')
    #     new_ioput.process_verify_json(json_str)
    #     return new_ioput
    def _serialize(self) -> JsonDict:
        return {KEY_VALUE: self.value, KEY_FROM_ADDR: self.from_addr, KEY_TO_ADDR: self.to_addr}

    def _unserialize(self, json_obj: JsonDict) -> None:
        self.value = json_obj[KEY_VALUE]
        self.from_addr = json_obj[KEY_FROM_ADDR]
        self.to_addr = json_obj[KEY_TO_ADDR]
