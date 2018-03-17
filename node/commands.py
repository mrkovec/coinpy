import logging
from typing import Any, Callable
# from typing import Iterator, List, Tuple, NewType, Dict, Callable, Any
from mypy_extensions import KwArg, Arg

from coinpy.core import JsonDict
from coinpy.core.crypto import Serializable
from coinpy.core.transaction import Transaction
from coinpy.core.block import Block



# import coinpy.node.peer as peer

# from coinpy.core.crypto import (
#     Serializable
# )
# from .node import Node

from coinpy.core.errors import (
    ValidationError
)



# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


CommandHandler = Callable[[Arg(Any), KwArg(Any)], None]

class Command(Serializable):
    name = 'undefined'
    def __init__(self, **params: Any) -> None:
        self.params = params
    def _serialize(self) -> JsonDict:
        return {
            'name': self.name,
            'params': self.params,
        }
    def validate(self) -> None:
        if self.name == 'undefined':
            raise ValidationError
    def _unserialize(self, comm_obj: JsonDict) -> None:
        self.name = comm_obj['name']
        self.params = comm_obj['params']
    @staticmethod
    def handler(ctx: Any, **kwargs: Any) -> None:
        raise NotImplementedError('Command.handler')





# CommandHandler = NewType('CommandHandler', Dict[str, Callable[[Arg(Any), KwArg(Any)], None]])



# class GreetCommand(Command):
#     name = 'great'
#     @staticmethod
#     def handler(p: Any, **kwargs:Any) -> None:
#         print(f'{GreetCommand.name} from {kwargs["source_msg"].from_addr}')

#
#
# class AnnounceTrxCommand(Command):
#     def __init__(self, trx: Transaction) -> None:
#         super().__init__('newtrx', {'trx': trx})
#

class AnnounceTransactionCommand(Command):
    name = 'newtrx'
    def __init__(self, trx: Transaction) -> None:
        super().__init__(trx=trx)
    @staticmethod
    def handler(ctx: Any, **kwargs:Any) -> None:
        logger.debug(f'running "{AnnounceTransactionCommand.name}" comand with {type(ctx)} {kwargs}')
        ctx.add_transaction(Transaction.unserialize(kwargs['trx']))

class AnnounceBlockCommand(Command):
    name = 'newblock'
    """Commnad for announcing new mined blocks.

    :param blk: mined block
    """
    def __init__(self, blk: Block) -> None:
        super().__init__(blk=blk)
    """Handler for received `Block``."""
    @staticmethod
    def handler(ctx: Any, **kwargs:Any) -> None:
        logger.debug(f'running "{AnnounceBlockCommand.name}" comand with {type(ctx)} {kwargs}')
        ctx.ext_add_block(Block.unserialize(kwargs['blk']))
