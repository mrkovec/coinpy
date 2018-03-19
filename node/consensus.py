from time import time
from typing import Dict

from coinpy.core.crypto import Pubkey, ID
from coinpy.core.block import Block
from coinpy.core.transaction import Transaction, Utils
from coinpy.core.errors import ConsensusError, BlockRulesError, TransactionRulesError

from coinpy.core.output import OutputID


class Rules(object):
    @staticmethod
    def block_valid_header(prev: Block, new: Block) -> None:
        if new.version == 1:
            if prev.height >= new.height or new.height - prev.height > 1:
                raise BlockRulesError('wrong height')
            if prev.time_stamp > time():
                raise BlockRulesError('wrong time_stamp')
            if prev.time_stamp > new.time_stamp:
                raise BlockRulesError('wrong time_stamp')

            Rules.block_valid_difficulty(new)
        else:
            raise ConsensusError('wrong block version')

    @staticmethod
    def block_valid_difficulty(blk: Block) -> None:
        for i in range(blk.difficulty):
            if bytes(blk.id)[i] != 0:
                raise BlockRulesError('wrong data')

    @staticmethod
    def block_valid_transactions(blk: Block) -> None:
        # for trx in blk.trxs_data.values():
        for trx in blk.transactions:
            Rules.transaction_valid_header(trx)

    @staticmethod
    def block_valid(prev: Block, new: Block) -> None:
        Rules.block_valid_header(prev, new)
        Rules.block_valid_transactions(new)


    @staticmethod
    # def transaction_valid_header(blk: Block, trx: Transaction) -> None:
    def transaction_valid_header(trx: Transaction) -> None:
        if trx.version == 1:
            if trx.time_stamp > time():
                raise TransactionRulesError('wrong time_stamp')
            # if trx.time_stamp > blk.time_stamp:
            #     raise TransactionRulesError('wrong time_stamp')

            # if type(trx) is CoinbaseTransaction:
            #     return
            if Utils.transaction_is_coinbase:
                return

            #  only inputs from the same pubaddr allowed
            pubaddrs = set(trx.inputs_data.keys())
            if len(pubaddrs) > 1:
                raise TransactionRulesError('more pubaddrs')

            if trx.signature_pubkey.pubaddr != pubaddrs.pop():
                raise TransactionRulesError('wrong pubaddr for pubkey')

            # valid signed transaction
            try:
                trx.verify_sign()
            except Exception as e:
                raise TransactionRulesError from e

            # sums of inputs vs outputs amounts
            sum_inp = sum(inp.amount for inp in trx.inputs_data.values())
            sum_outp = sum(outp.amount for outp in trx.outputs)
            if sum_outp > sum_inp:
                raise TransactionRulesError('wrong trx balance')
        else:
            raise ConsensusError('wrong trx version')
