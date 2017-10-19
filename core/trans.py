from time import time
from json import loads as json_loads
from typing import List, Dict, Any, Optional
JsonDict = Dict[str, Any]

from .ioput import IOput
from .crypto import SerializableObject, Hash

KEY_TIME_STAMP = 'time_stamp'
KEY_INPS = 'inps'
KEY_OUTPS = 'outps'

class Trans(SerializableObject):
    def __init__(self, time_stamp: Optional[float] = None) -> None:
        self._id: Optional[Hash] = None
        if time_stamp is None:
            self.time_stamp = time()
        else:
            self.time_stamp = time_stamp
        self.inps: List[IOput] = []
        self.outps: List[IOput] = []

    @classmethod
    def from_obj(cls, json_obj: JsonDict) -> 'Trans':
        new_trx = cls()
        new_trx.verify_and_unserialize(json_obj)
        return new_trx

    @classmethod
    def from_json(cls, json_str: str) -> 'Trans':
        return cls.from_obj(json_loads(json_str))

    def _serialize(self) -> JsonDict:
        return {KEY_TIME_STAMP: self.time_stamp, KEY_INPS: self.inps, KEY_OUTPS: self.outps}

    def _unserialize(self, json_obj: JsonDict) -> None:
        self.time_stamp = json_obj[KEY_TIME_STAMP]
        for inp in json_obj[KEY_INPS]:
             self.add_inp(IOput.from_obj(inp))
        for outp in json_obj[KEY_OUTPS]:
            self.add_outp(IOput.from_obj(outp))

    def add_inp(self, inp: IOput) -> None:
        self.inps.append(inp)

    def add_outp(self, outp: IOput) -> None:
        self.outps.append(outp)
