from time import time

from coinpy.core.block import Block
from coinpy.core.errors import ConsensusError, BlockRulesError

class Rules(object):
    @staticmethod
    def valid_block(prev: Block, new: Block) -> None:
        if new.version == 1:
            if prev.height >= new.height:
                raise BlockRulesError('height')
            if prev.time_stamp >= time():
                raise BlockRulesError('time_stamp')
            if prev.time_stamp >= new.time_stamp:
                raise BlockRulesError('time_stamp')
            Rules.verify_block_data(new)
        else:
            raise ConsensusError('block version')

    @staticmethod
    def verify_block_data(blk: Block) -> None:
        for i in range(blk.difficulty):
            if bytes(blk.id)[i] != 0:
                raise BlockRulesError('data')
