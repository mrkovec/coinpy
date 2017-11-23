import logging
from typing import Iterator, List, Tuple, NewType, Dict, Callable, Any
from coinpy.core import JsonDict

from coinpy.core.transaction import Transaction
from coinpy.core.block import Block

from coinpy.core.crypto import (
    Serializable
)
from coinpy.core.errors import (
    ValidationError
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Command(Serializable):
    def __init__(self, name: str, kwargs: Dict[str, Any] = {}) -> None:
        self.name = name
        self.kwargs = kwargs
    def _serialize(self) -> JsonDict:
        return {
            'name': self.name,
            'kwargs': self.kwargs,
        }
    def validate(self) -> None:
        if self.name is None:
            raise ValidationError
    def _unserialize(self, comm_obj: JsonDict) -> None:
        self.name = comm_obj['name']
        self.kwargs = comm_obj['kwargs']

class GreetCommand(Command):
    def __init__(self) -> None:
        super().__init__('greet')

class AnnounceTrxCommand(Command):
    def __init__(self, trx: Transaction) -> None:
        super().__init__('newtrx', {'trx': trx})

class AnnounceBlockCommand(Command):
    def __init__(self, blk: Block) -> None:
        pass
