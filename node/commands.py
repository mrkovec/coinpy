import logging
from typing import Any, Callable, List
# from typing import Iterator, List, Tuple, NewType, Dict, Callable, Any
from mypy_extensions import KwArg, Arg

from coinpy.core import JsonDict
from coinpy.core.crypto import Serializable
from coinpy.core.transaction import Transaction
from coinpy.core.block import Block

from coinpy.core.errors import (
    ValidationError
)

logger = logging.getLogger(__name__)

CommandHandler = Callable[[Arg(Any, 'ctx'), KwArg(Any)], None]

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


class GreetCommand(Command):
    name = 'greet'
    def __init__(self, blk_height: int) -> None:
        super().__init__(height=blk_height)
    @staticmethod
    def handler(ctx: Any, **kwargs:Any) -> None:
        logger.debug(f'running "{GreetCommand.name}" comand with {type(ctx)}, {kwargs}')
        ctx.command_greet_handler(kwargs['height'], tuple(kwargs['source_msg'].from_addr))


class InfoCommand(Command):
    name = 'info'
    def __init__(self, blocks_insert: List[Block]) -> None:
        super().__init__(blocks_insert=blocks_insert)
    @staticmethod
    def handler(ctx: Any, **kwargs:Any) -> None:
        logger.debug(f'running "{InfoCommand.name}" comand with {type(ctx)}, {kwargs}')
        ctx.command_info_handler(kwargs['blocks_insert'])


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
        ctx.block_add_to_blockchain(Block.unserialize(kwargs['blk']))
