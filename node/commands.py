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


CommandHandler = Callable[[Arg(Any, 'ctx'), KwArg(Any)], None]
# CommandHandler = Callable[[Arg(Any), KwArg(Any)], None]

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
# class GreetCommand(Command):
#     name = 'greet'
#     def __init__(self, blk_height: int) -> None:
#         super().__init__(height=blk_height)
#     @staticmethod
#     def handler(ctx: Any, **kwargs:Any) -> None:
#         logger.debug(f'running "{GreetCommand.name}" comand with {type(ctx)} {kwargs}')
#         ctx.command_greet(kwargs['height'], kwargs['source_msg'].from_addr)
#         # ctx.__peer.commnad_send(kwargs['source_msg'].from_addr, ReplyGreetCommand(ctx.__ledger[-1].height))
#         # ctx.add_transaction(Transaction.unserialize(kwargs['trx']))
#
# class ReplyGreetCommand(Command):
#     name = 'regreet'
#     def __init__(self, blk_height: int) -> None:
#         super().__init__(height=blk_height)
#     @staticmethod
#     def handler(ctx: Any, **kwargs:Any) -> None:
#         logger.debug(f'running "{ReplyGreetCommand.name}" comand with {type(ctx)} {kwargs}')
#         ctx.command_replygreet()
#         # ctx.add_transaction(Transaction.unserialize(kwargs['trx']))
#
# class AnnounceTransactionCommand(Command):
#     name = 'newtrx'
#     def __init__(self, trx: Transaction) -> None:
#         super().__init__(trx=trx)
#     @staticmethod
#     def handler(ctx: Any, **kwargs:Any) -> None:
#         logger.debug(f'running "{AnnounceTransactionCommand.name}" comand with {type(ctx)} {kwargs}')
#         ctx.add_transaction(Transaction.unserialize(kwargs['trx']))

class AnnounceBlockCommand(Command):
    name = 'newblock'
    """Commnad for announcing new mined blocks.

    :param blk: mined block
    """
    def __init__(self, blk: Block) -> None:
        super().__init__(blk=blk)
    """Handler for received `Block`."""
    @staticmethod
    def handler(ctx: Any, **kwargs:Any) -> None:
        logger.debug(f'running "{AnnounceBlockCommand.name}" command with {type(ctx)} {kwargs}')
        ctx.block_add(Block.unserialize(kwargs['blk']))
