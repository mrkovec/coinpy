from typing import Optional
from .crypto import CryptoObj, Hash

KEY_VALUE = 'val'
KEY_FROM_ADDR = 'from'
KEY_TO_ADDR = 'to'

class IOput(CryptoObj):
    def __init__(self, init_val: float, init_from: str, init_to: str) -> None:
        self.id: Optional[Hash] = None
        self.value = init_val
        self.from_addr = init_from
        self.to_addr = init_to

    @classmethod
    def from_json_obj(cls, json_obj: object) -> 'IOput':
        new_ioput = cls(-1,'','')
        new_ioput.process_verify_obj(json_obj)
        return new_ioput

    # @classmethod
    # def from_json_str(cls, json_str: str) -> 'IOput':
    #     new_ioput = cls(-1,'','')
    #     new_ioput.process_verify_json(json_str)
    #     return new_ioput

    def _set_data(self, id: Hash, data: object) -> None:
        self.id = id
        self.value = data[KEY_VALUE]
        self.from_addr = data[KEY_FROM_ADDR]
        self.to_addr = data[KEY_TO_ADDR]

    def _prepare_data(self) -> object:
        return {KEY_VALUE: self.value, KEY_FROM_ADDR: self.from_addr, KEY_TO_ADDR: self.to_addr}
