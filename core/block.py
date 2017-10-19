from time import time
from json import loads as json_loads
from typing import List, Dict, Any, Optional
JsonDict = Dict[str, Any]

from .trans import Trans, KEY_TIME_STAMP
from .crypto import SerializableObject, Hash


KEY_PREV_BLOCK = 'prev_block'
KEY_TRXS = 'trxs'

class Block(SerializableObject):
    def __init__(self, time_stamp: Optional[float] = None) -> None:
        self._id: Optional[Hash] = None
        self.prev_block_hash: Optional[Hash] = None
        if time_stamp is None:
            self.time_stamp = time()
        else:
            self.time_stamp = time_stamp
        self.trxs: List[Trans] = []

    @classmethod
    def from_obj(cls, json_obj: JsonDict) -> 'Block':
        new_blk = cls()
        new_blk.verify_and_unserialize(json_obj)
        return new_blk

    @classmethod
    def from_json(cls, json_str: str) -> 'Block':
        return cls.from_obj(json_loads(json_str))

    def create_next_block(self) -> 'Block':
        new_blk = Block()
        new_blk.prev_block_hash = self._id
        return new_blk

    def _serialize(self) -> JsonDict:
        prev_h = ''
        if self.prev_block_hash is not None:
            prev_h = self.prev_block_hash.str_
        return {KEY_TIME_STAMP: self.time_stamp, KEY_PREV_BLOCK: prev_h, KEY_TRXS: self.trxs}

    def _unserialize(self, json_obj: JsonDict) -> None:
        self.prev_block_hash = Hash.from_str(json_obj[KEY_PREV_BLOCK])
        self.time_stamp = json_obj[KEY_TIME_STAMP]
        for trx in json_obj[KEY_TRXS]:
            self.add_trx(Trans.from_obj(trx))

    def add_trx(self, trx: Trans) -> None:
            self.trxs.append(trx)
