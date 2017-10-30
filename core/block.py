import time
import json

from . import (
    List, JsonDict
)
from .trans import (
    Trans, TransID
)
from .crypto import (
    Hash, Serializable, ID
)

KEY_BLOCK_TIME_STAMP = 'time_stamp'
KEY_BLOCK_PREV_BLOCK = 'prev_block'
KEY_BLOCK_TRXS = 'trxs'

class BlockHash(Hash, digest_size = 33, person = b'BlockHash'):
    pass

class BlockID(ID, id_hash = BlockHash):
    @classmethod
    def from_obj(cls, json_obj: JsonDict) -> 'BlockID':
        blk_new = cls()
        blk_new.unserialize(json_obj)
        return blk_new

class Block(Serializable):
    __id: BlockID

    def __init__(self, time_stamp: float = None, prev_blk: 'Block' = None) -> None:
        self.__id = BlockID()
        if prev_blk is not None:
            self.prev_block = prev_blk.id
        else:
            self.prev_block = BlockID(b'')
        if time_stamp is None:
            self.time_stamp = time.time()
        else:
            self.time_stamp = time_stamp
        self.trxs: List[TransID] = []

    def serialize(self) -> JsonDict:
        return {KEY_BLOCK_TIME_STAMP: self.time_stamp, KEY_BLOCK_PREV_BLOCK: self.prev_block, KEY_BLOCK_TRXS: self.trxs}

    def unserialize(self, json_obj: JsonDict) -> None:
        self.time_stamp = json_obj[KEY_BLOCK_TIME_STAMP]
        self.prev_block = BlockID.from_obj(json_obj[KEY_BLOCK_PREV_BLOCK])
        for trx in json_obj[KEY_BLOCK_TRXS]:
            self.add_trx(TransID.from_obj(trx))

    @classmethod
    def from_json(cls, json_str: str) -> 'Block':
        new_blk = cls()
        new_blk.unserialize_json(json_str)
        return new_blk

    @property
    def id(self) -> BlockID:
        self.__id.digest(self.to_json().encode('utf-8'))
        return self.__id

    # @classmethod
    # def from_obj(cls, json_obj: JsonDict) -> 'Block':
    #     new_blk = cls()
    #     new_blk.verify_and_unserialize(json_obj)
    #     return new_blk
    #
    # @classmethod
    # def from_json(cls, json_str: str) -> 'Block':
    #     return cls.from_obj(json_loads(json_str))
    #
    # def create_next_block(self) -> 'Block':
    #     new_blk = Block()
    #     new_blk.prev_block_id = self.id
    #     return new_blk
    #
    # def _serialize(self) -> JsonDict:
    #     # prev_h = ''
    #     # if self.prev_block_hash is not None:
    #     # prev_h =
    #     return {KEY_TIME_STAMP: self.time_stamp, KEY_PREV_BLOCK: bytes_to_str(self.prev_block_id), KEY_TRXS: self.trxs}
    #
    # def _unserialize(self, json_obj: JsonDict) -> None:
    #     self.prev_block_id = str_to_bytes(json_obj[KEY_PREV_BLOCK])
    #     self.time_stamp = json_obj[KEY_TIME_STAMP]
    #     for trx in json_obj[KEY_TRXS]:
    #         self.add_trx(Trans.from_obj(trx))

    def add_trx(self, trx: TransID) -> None:
            self.trxs.append(trx)
