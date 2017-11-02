import time
import json
import logging


from . import (
    List, JsonDict, NewType
)
from .trans import (
    Trans, TransID
)
from .crypto import (
    Hash, Serializable, ID, Utils
)
from .errors import DataError, ValidationError
# from .output import OutputID

logger = logging.getLogger(__name__)

KEY_BLOCK_TIME_STAMP = 'time_stamp'
KEY_BLOCK_PREV_BLOCK = 'prev_block'
KEY_BLOCK_TRXS = 'trxs'

BlockHash = Hash(digest_size = 33, person = b'BlockHash')
BlockID = NewType('BlockID', ID)

# class BlockHash(Hash, digest_size = 33, person = b'BlockHash'):
#     pass
#
# class BlockID(ID, id_hash = BlockHash):
#     @classmethod
#     def from_obj(cls, json_obj: JsonDict) -> 'BlockID':
#         blk_new = cls()
#         blk_new.unserialize(json_obj)
#         return blk_new

class Block(Serializable):
    # __id: BlockID

    def __init__(self, time_stamp: float, prev_blk: 'Block', trxs: List[TransID] = None) -> None:
        prev_blk.validate()
        self.prev_block_id = prev_blk.id
        self.time_stamp = time_stamp
        self.trxs = trxs
        self.__id = BlockID(ID(BlockHash.digest(str(self).encode('utf-8'))))

    def _serialize(self) -> JsonDict:
        return {
            KEY_BLOCK_TIME_STAMP: self.time_stamp,
            KEY_BLOCK_PREV_BLOCK: self.prev_block_id,
            KEY_BLOCK_TRXS: self.trxs
        }

    def _unserialize(self, json_obj: JsonDict) -> None:
        try:
            self.time_stamp = json_obj[KEY_BLOCK_TIME_STAMP]
            self.prev_block_id = BlockID(ID(Utils.str_to_bytes(json_obj[KEY_BLOCK_PREV_BLOCK])))
            self.trxs = []
            for trx in json_obj[KEY_BLOCK_TRXS]:
                self.trxs.append(TransID(ID(Utils.str_to_bytes(trx))))
        except Exception as e:
            raise DataError(str(e)) from e
        self.__id = BlockID(ID(BlockHash.digest(str(self).encode('utf-8'))))


    def validate(self) -> None:
        if (self.time_stamp is None or self.prev_block_id is None or self.trxs is None
                or len(self.trxs) == 0):
            raise ValidationError
    # @classmethod
    # def from_json(cls, json_str: str) -> 'Block':
    #     new_blk = cls()
    #     new_blk.unserialize_json(json_str)
    #     return new_blk

    @property
    def id(self) -> BlockID:
        # self.__id.digest(self.to_json().encode('utf-8'))
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

    # def add_trx(self, trx: TransID) -> None:
    #         self.trxs.append(trx)

class GenesisBlock(Block):
    def __init__(self) -> None:
        self.prev_block_id = BlockID(ID(b''))
        self.time_stamp = 123
        self.trxs = []
        self.__id = BlockID(ID(b'GenesisBlock'))

    def validate(self) -> None:
        pass

    @property
    def id(self) -> BlockID:
        return self.__id

GENESIS_BLOCK =  GenesisBlock()
