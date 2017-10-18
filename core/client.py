from typing import List
import json
from core.block import Block
from core.trans import Transaction, trx_from_json_obj

GENESIS_BLOCK = Block("")

class Client:
    def __init__(self) -> None:
        self.block_chain: List[Block] = [GENESIS_BLOCK]
        self.unproc_trxs: List[Transaction] = []

    def process_new_trx(self, trx_json: str) -> None:
        new_trx = trx_from_json_obj(json.loads(trx_json))
        self.unproc_trxs.append(new_trx)
