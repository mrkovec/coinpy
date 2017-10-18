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
    def from_json_obj(cls, json_obj: object) -> 'Block':
        new_blk = cls('')
        new_blk.process_verify_obj(json_obj)
        return new_blk

    def add_trx(self, trx: Trans) -> None:
            self.trxs.append(trx)

    def _prepare_data(self) -> object:
        return {KEY_TIME_STAMP: self.time_stamp, KEY_PREV_BLOCK: self.prev_block, KEY_TRXS: self.trxs}

    def _set_data(self, id: Hash, data: object) -> None:
        self.id = id
        self.prev_block = data[KEY_PREV_BLOCK]
        self.time_stamp = data[KEY_TIME_STAMP]
        for trx in data[KEY_TRXS]:
            self.add_trx(Trans.from_json_obj(trx))



# def block_from_json_obj(json_obj) -> Block:
#     try:
#         for block_hash, block_data in json_obj.items():
#             new_block = Block(block_data[KEY_PREV_BLOCK])
#             new_block.time_stamp = block_data[KEY_TIME_STAMP]
#             for trx in block_data[KEY_TRXS]:
#                 new_block.add_trx(trx_from_json_obj(trx))
#             if new_block.check_hash(block_hash):
#                 return new_block
#     except:
#         raise DataError('incorrect block data')
#     raise HashError('incorrect block data')


# def block_from_json(json_string: str) -> Optional[Block]:
#     return block_from_json_dict(json.loads(json_string))
