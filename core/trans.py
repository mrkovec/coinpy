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
    def from_json_obj(cls, json_obj: object) -> 'Trans':
        new_trx = cls()
        new_trx.process_verify_obj(json_obj)
        return new_trx

    def add_inp(self, inp: IOput) -> None:
        self.inps.append(inp)

    def add_outp(self, outp: IOput) -> None:
        self.outps.append(outp)

    def _prepare_data(self) -> object:
        return {KEY_TIME_STAMP: self.time_stamp, KEY_INPS: self.inps, KEY_OUTPS: self.outps}

    def _set_data(self, id: Hash, data: object) -> None:
        self.id = id
        self.time_stamp = data[KEY_TIME_STAMP]
        for inp in data[KEY_INPS]:
             self.add_inp(IOput.from_json_obj(inp))
        for outp in data[KEY_OUTPS]:
            self.add_outp(IOput.from_json_obj(outp))

# def trx_from_json_obj(json_obj) -> Transaction:
#     try:
#         for trx_hash, trx_data in json_obj.items():
#             new_trx = Transaction()
#             new_trx.time_stamp = trx_data[KEY_TIME_STAMP]
#             for inp in trx_data[KEY_INPS]:
#                 new_trx.add_input(ioput_from_json_obj(inp))
#             for outp in trx_data[KEY_OUTPS]:
#                 new_trx.add_output(ioput_from_json_obj(outp))
#             if new_trx.check_hash(trx_hash):
#                 return new_trx
#     except:
#         raise DataError('incorrect trx data')
#     raise HashError('incorrect trx data')

# def trx_from_json(json_string: str) -> Optional[Transaction]:
#     return trx_from_json_dict(json.loads(json_string))
