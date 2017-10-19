from typing import List

from .core.block import Block
from .core.trans import Trans

GENESIS_BLOCK = Block.from_obj(
    {
       "avYSgAigKRaL82Vo5tKVUp1VgpIO/Hykz06rLq1u/K9pMI6cpbP2viavhYSyBdVnR4yIfL4m8bLWAhllS2277Q==":{
          "time_stamp":1508352582.3449388,
          "prev_block":"",
          "trxs":[]
        }
    })

class Client:
    def __init__(self) -> None:
        self.block_chain: List[Block] = [GENESIS_BLOCK]
        self.unproc_trxs: List[Trans] = []

    # def process_new_trx(self, trx_json: str) -> None:
    #     new_trx = trx_from_json_obj(json.loads(trx_json))
    #     self.unproc_trxs.append(new_trx)
