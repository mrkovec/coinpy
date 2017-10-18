from typing import List, Optional
from time import time

from .ioput import IOput
from .crypto import CryptoObj, Hash
# from .errors import Error

KEY_TIME_STAMP = 'time_stamp'
KEY_INPS = 'inps'
KEY_OUTPS = 'outps'

class Trans(CryptoObj):
    def __init__(self, time_stamp: Optional[float] = None) -> None:
        self.id: Optional[Hash] = None
        if time_stamp is None:
            self.time_stamp = time()
        else:
            self.time_stamp = time_stamp
        self.inps: List[IOput] = []
        self.outps: List[IOput] = []

    @classmethod
    def from_obj(cls, json_obj: object) -> 'Trans':
        new_trx = cls()
        new_trx.process_verify_obj(json_obj)
        return new_trx

    @classmethod
    def from_json(cls, json_str: str) -> 'Trans':
        new_trx = cls()
        new_trx.process_verify_json(json_str)
        return new_trx

    def _prepare_data(self) -> object:
        return {KEY_TIME_STAMP: self.time_stamp, KEY_INPS: self.inps, KEY_OUTPS: self.outps}

    def _set_data(self, id: Hash, data: object) -> None:
        self.id = id
        self.time_stamp = data[KEY_TIME_STAMP]
        for inp in data[KEY_INPS]:
             self.add_inp(IOput.from_obj(inp))
        for outp in data[KEY_OUTPS]:
            self.add_outp(IOput.from_obj(outp))

    def add_inp(self, inp: IOput) -> None:
        self.inps.append(inp)

    def add_outp(self, outp: IOput) -> None:
        self.outps.append(outp)
