from typing import List, Optional
from time import time
from .trans import Trans, KEY_TIME_STAMP
from .crypto import CryptoObj, Hash
# from .errors import HashError, DataError

KEY_PREV_BLOCK = 'prev_block'
KEY_TRXS = 'trxs'

class Block(CryptoObj):
    def __init__(self, prev_block_hash: str, time_stamp: Optional[float] = None) -> None:
        self.id: Optional[Hash] = None
        self.prev_block = prev_block_hash
        if time_stamp is None:
            self.time_stamp = time()
        else:
            self.time_stamp = time_stamp
        self.trxs: List[Trans] = []

    @classmethod
    def from_obj(cls, json_obj: object) -> 'Block':
        new_blk = cls('')
        new_blk.process_verify_obj(json_obj)
        return new_blk

    @classmethod
    def from_json(cls, json_str: str) -> 'Trans':
        new_blk = cls('')
        new_blk.process_verify_json(json_str)
        return new_blk

    def _prepare_data(self) -> object:
        return {KEY_TIME_STAMP: self.time_stamp, KEY_PREV_BLOCK: self.prev_block, KEY_TRXS: self.trxs}

    def _set_data(self, id: Hash, data: object) -> None:
        self.id = id
        self.prev_block = data[KEY_PREV_BLOCK]
        self.time_stamp = data[KEY_TIME_STAMP]
        for trx in data[KEY_TRXS]:
            self.add_trx(Trans.from_obj(trx))

    def add_trx(self, trx: Trans) -> None:
            self.trxs.append(trx)
