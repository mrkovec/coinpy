import logging
import json
from typing import Iterator, List, Tuple, NewType, Dict, Callable, Any, Type, Iterable
from mypy_extensions import KwArg, Arg
import asyncio

from coinpy.core import JsonDict
from coinpy.core.crypto import Serializable

# import coinpy.node.node as node
# import coinpy.node.commands as commands

    # import coinpy.node.node as node
from coinpy.core.errors import (
    ValidationError
)
from .commands import (
    Command
)

VERSION = 1

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

PeerAddr = NewType('PeerAddr', Tuple[str, int])

# PeerAddr = Tuple[str, int]
class Message(Serializable):
    def __init__(self, comm: Command, from_addr: PeerAddr) -> None:
        self.ver = VERSION
        self.command = comm
        self.from_addr = from_addr
    def _serialize(self) -> JsonDict:
        return {
            'ver': self.ver,
            'command': self.command,
            'from_addr': self.from_addr,
        }
    def validate(self) -> None:
        if self.ver is None or self.command is None or self.from_addr is None:
            raise ValidationError
    def _unserialize(self, comm_obj: JsonDict) -> None:
        self.ver = comm_obj['ver']
        self.command = Command.unserialize(comm_obj['command'])
        self.from_addr = comm_obj['from_addr']
        # append source message to command parameters
        # self.command.params['source_msg'] = self
    @property
    def raw(self) -> bytes:
        return str(self).encode('utf-8')


class RawMessage(object):
    def __init__(self, msg_raw: bytes, neighbor_addr: PeerAddr) -> None:
        self.__msg_json = msg_raw.decode('utf-8')
        self.__neighbor_addr = neighbor_addr
    @property
    def message(self) -> Message:
        m = Message.unserialize_json(self.__msg_json)
        if m.ver != VERSION:
            raise ValidationError('incorrect msg version')
        if m.from_addr[0] != self.__neighbor_addr[0]:
            raise ValidationError('incorrect msg adrress')
        return m

class PeerListener(asyncio.DatagramProtocol):
    def __init__(self, msg_queue: asyncio.Queue, loop: asyncio.AbstractEventLoop) -> None: # type: ignore
        self.__io_loop = loop
        self.__msg_queue = msg_queue
    def connection_made(self, transport: asyncio.DatagramTransport) -> None: # type: ignore
        self.transport = transport
    def datagram_received(self, msg_raw:bytes, addr: PeerAddr) -> None: # type: ignore
        message = msg_raw.decode()
        asyncio.ensure_future(self.__msg_queue.put(RawMessage(msg_raw, addr)), loop=self.__io_loop)
        logger.debug(f'receiving {message} from {addr}')
    def error_received(self, exc: OSError) -> None: # type: ignore
        logger.error(str(exc))


class PeerSender(asyncio.DatagramProtocol):
    def __init__(self, msg: Message) -> None:
        self.message = msg
    def connection_made(self, transport: asyncio.DatagramTransport) -> None: # type: ignore
        transport.sendto(self.message.raw)
    def error_received(self, exc: OSError) -> None: # type: ignore
        logger.error(str(exc))

class Peer(object):
    def __init__(self, loop: asyncio.AbstractEventLoop, addr: PeerAddr ) -> None:
        self.addr = addr
        self.__neighbors_addr: List[PeerAddr] = []
        # self.__registered_commands: Dict[str, Tuple[Any, CommandHandler]] = {}
        self.__io_loop = loop

    async def start(self) ->None:
        logger.info(f'starting peer {self.addr}')
        self.__msg_queue: asyncio.Queue = asyncio.Queue(loop=self.__io_loop) # type: ignore

        # listener = self.__io_loop.create_datagram_endpoint(lambda: PeerListener(self.__msg_queue, self.__io_loop), local_addr=self.addr)
        # self.transport, _ = self.__io_loop.run_until_complete(listener)
        logger.debug('initializing listener')
        self.__transport, _ = await self.__io_loop.create_datagram_endpoint(lambda: PeerListener(self.__msg_queue, self.__io_loop), local_addr=self.addr)
        # self.__transport, _ = await self.__io_loop.create_task(self.__io_loop.create_datagram_endpoint(lambda: PeerListener(self.__msg_queue, self.__io_loop), local_addr=self.addr))
        # self.__msg_handle_task = self.__io_loop.create_task(self.msg_handle())

        # asyncio.ensure_future(self.process_msg(), loop=self.io_loop)


    async def stop(self) -> None:
        logger.info(f'stopping peer {self.addr}')
        # cancel msg_process
        # self.__msg_handle_task.cancel()
        # await self.__msg_handle_task
        self.__transport.close()

    async def msg_send(self, addr: PeerAddr, msg: Message) -> None:
        logger.debug(f'sending msg {msg} to {addr}')
        # self.__io_loop.create_task(self.__io_loop.create_datagram_endpoint(lambda: PeerSender(msg), remote_addr=addr))
        await self.__io_loop.create_datagram_endpoint(lambda: PeerSender(msg), remote_addr=addr)

    async def msg_receive(self) -> Message:
        msg_raw = await self.__msg_queue.get()
        self.__msg_queue.task_done()
        return msg_raw.message

    async def msg_handle(self) -> None:
        logger.debug('waiting for messages')
        while True:
            try:
                # msg_raw = await self.__msg_queue.get()
                # msg = msg_raw.message
                # msg = await self.msg_receive()
                # logger.debug(f'executing "{msg.command}"{self.__registered_commands[msg.command.name]}')
                # ctx, comm = self.__registered_commands[msg.command.name]
                # comm(ctx, **{**msg.command.params, 'source_msg': msg})
                self.__msg_queue.task_done()
            except asyncio.CancelledError:
                # logger.info("waiting for messages stopped")
                return
            except Exception as e:
                logger.exception(str(e))

    # def start(self, run = False) -> None:
    #     listener = self.io_loop.create_datagram_endpoint(lambda: PeerListener(self.__msg_queue, self.io_loop), local_addr=self.addr)
    #     transport, _ = self.io_loop.run_until_complete(listener)
    #     self.io_loop.create_task(self.process_msg())
    #     # self.send_bulk_commnad(GreetCommand())
    #     if run:
    #         try:
    #             self.io_loop.run_until_complete(self.process_msg())
    #         except KeyboardInterrupt:
    #             pass
    #         self.stop()
    #     # transport.close()
    #     # self.io_loop.close()


    def neighbors_add(self, ns: List[PeerAddr]) -> None:
        for n in ns:
            if n not in self.__neighbors_addr:
                logger.debug(f'adding peer neighbor {n}')
                self.__neighbors_addr.append(n)





    # def commnad_direct(self, comm: Command) -> None:
    #     msg = Message(comm, self.addr)
    #     self.__msg_queue.put(RawMessage(msg.raw, self.addr))
