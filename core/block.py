"""Block functionality."""

import time
import json
import logging
from typing import (
    List, NewType, Optional
)

from . import JsonDict

from .transaction import (
    Transaction, TransactionID
)
from .crypto import (
    Hash, Serializable, ID, Utils
)
from .errors import (
    DataError, ValidationError
)


logger = logging.getLogger(__name__)

BLOCK_VERSION = 1

KEY_BLOCK_VERSION = 'ver'
KEY_BLOCK_NONCE = 'n'
KEY_BLOCK_TIME_STAMP = 'time_stamp'
KEY_BLOCK_PREV_BLOCK = 'prev_block'
KEY_BLOCK_HEIGHT = 'height'
KEY_BLOCK_DIFFICULTY = 'dif'
KEY_BLOCK_TRXS = 'trxs'

BlockHash = Hash(digest_size = 33, person = b'BlockHash')
BlockID = NewType('BlockID', ID)

class Block(Serializable):
    def __init__(self, time_stamp: float, prev_blk: 'Block', trxs: List[Transaction], nonce: int = 0) -> None:
        self.version = BLOCK_VERSION
        self.nonce = nonce
        prev_blk.validate()
        self.prev_block_id = prev_blk.id
        self.height: int = prev_blk.height + 1
        self.difficulty: int = prev_blk.difficulty
        self.time_stamp = time_stamp
        self.transactions = trxs

    def _serialize(self) -> JsonDict:
        return {
            KEY_BLOCK_VERSION: self.version,
            KEY_BLOCK_NONCE: self.nonce,
            KEY_BLOCK_TIME_STAMP: self.time_stamp,
            KEY_BLOCK_PREV_BLOCK: self.prev_block_id,
            KEY_BLOCK_HEIGHT: self.height,
            KEY_BLOCK_DIFFICULTY: self.difficulty,
            KEY_BLOCK_TRXS: self.transactions
        }

    def _unserialize(self, json_obj: JsonDict) -> None:
        try:
            self.time_stamp = json_obj[KEY_BLOCK_TIME_STAMP]
            self.version = json_obj[KEY_BLOCK_VERSION]
            self.nonce = json_obj[KEY_BLOCK_NONCE]
            self.prev_block_id = BlockID(ID(Utils.str_to_bytes(json_obj[KEY_BLOCK_PREV_BLOCK])))
            self.height = json_obj[KEY_BLOCK_HEIGHT]
            self.difficulty = json_obj[KEY_BLOCK_DIFFICULTY]
            self.transactions = []
            for trx in json_obj[KEY_BLOCK_TRXS]:
                self.transactions.append(Transaction.unserialize(trx))
        except Exception as e:
            raise DataError(str(e)) from e


    def validate(self) -> None:
        if (self.time_stamp is None or self.prev_block_id is None or self.transactions is None
                or len(self.transactions) == 0):
            raise ValidationError

    @property
    def id(self) -> BlockID:
        return BlockID(ID(BlockHash.digest(str(self).encode('utf-8'))))

class GenesisBlock(Block):
    def __init__(self, difficulty: int, nonce: int, time: float) -> None:
        self.version = BLOCK_VERSION
        self.nonce = nonce
        self.prev_block_id = BlockID(ID(b''))
        self.time_stamp = time
        self.height = 0
        self.difficulty = difficulty
        self.transactions = []

    def validate(self) -> None:
        pass

    @property
    def id(self) -> BlockID:
        return BlockID(ID(BlockHash.digest(str(self).encode('utf-8'))))

GENESIS_BLOCK =  GenesisBlock(3, 9821603, 1523724808.9048173)
