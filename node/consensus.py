from time import time
from typing import Dict

from coinpy.core.block import Block
from coinpy.core.trans import Trans
from coinpy.core.errors import ConsensusError, BlockRulesError, TransRulesError

class Rules(object):
    @staticmethod
    def valid_block(prev: Block, new: Block) -> None:
        if new.version == 1:
            if prev.height >= new.height:
                raise BlockRulesError('height')
            if prev.time_stamp > time():
                raise BlockRulesError('time_stamp')
            if prev.time_stamp > new.time_stamp:
                raise BlockRulesError('time_stamp')
            Rules.verify_difficulty(new)
            for trx in new.trx_dta.values():
                Rules.valid_trans(new, trx)
        else:
            raise ConsensusError('block version')

    @staticmethod
    def verify_difficulty(blk: Block) -> None:
        for i in range(blk.difficulty):
            if bytes(blk.id)[i] != 0:
                raise BlockRulesError('data')

    @staticmethod
    def valid_trans(blk: Block, trx: Trans) -> None:
        if trx.version == 1:
            if trx.time_stamp > time():
                raise TransRulesError('time_stamp')
            if trx.time_stamp > blk.time_stamp:
                raise TransRulesError('time_stamp')

            # inps_ids = set(self.inps)
            # if len(inps_ids) > 1:
            #     raise ValidationError
            #
            # self.signature_pubkey
            # vk.verify(self.sgn, b'abc')
        else:
            raise ConsensusError('trx version')
