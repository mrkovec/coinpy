import logging
import json
from typing import Iterator, List, Tuple, NewType, Dict, Callable, Any, Type, Iterable
from mypy_extensions import KwArg, Arg
import asyncio

from coinpy.core import JsonDict
from coinpy.core.crypto import Serializable

# import coinpy.node.node as node
# import coinpy.node.commands as commands
from .commands import (
        Command, CommandHandler
)
    # import coinpy.node.node as node
from coinpy.core.errors import (
    ValidationError
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
    def __init__(self, addr: PeerAddr, loop: asyncio.AbstractEventLoop) -> None:
        logger.info(f'starting peer {addr}')
        self.addr = addr
        self.__neighbors_addr: List[PeerAddr] = []
        self.__registered_commands: Dict[str, Tuple[Any, CommandHandler]] = {}

        self.__io_loop = loop
        self.__msg_queue: asyncio.Queue = asyncio.Queue(loop=self.__io_loop) # type: ignore

        logger.debug('initializing listener')
        listener = self.__io_loop.create_datagram_endpoint(lambda: PeerListener(self.__msg_queue, self.__io_loop), local_addr=self.addr)
        self.transport, _ = self.__io_loop.run_until_complete(listener)
        # asyncio.ensure_future(self.process_msg(), loop=self.io_loop)
        self.__procmsg_task = self.__io_loop.create_task(self.msg_process())

    def stop(self) -> None:
        logger.info(f'stopping peer {self.addr}')
        # pending = asyncio.Task.all_tasks(loop=self.io_loop)
        # for task in pending:
        #     logging.debug("canceling %s: %s", task, task.cancelled())
        #     task.cancel()
        # try:
        #     self.io_loop.run_until_complete(asyncio.gather(*pending))
        # except asyncio.CancelledError: # Any other exception would be bad
        # # except:
        #     for task in pending:
        #         logging.debug("Cancelled %s: %s", task, task.cancelled())
        # self.__msg_queue.close()

        # cancel msg proccessing
        self.__procmsg_task.cancel()
        # self.__io_loop.run_until_complete(self.procmsg_task)
        self.transport.close()

    def msg_send(self, addr: PeerAddr, msg: Message) -> None:
        logger.debug(f'sending msg {msg} to {addr}')
        self.__io_loop.create_task(self.__io_loop.create_datagram_endpoint(lambda: PeerSender(msg), remote_addr=addr))

    async def msg_process(self) -> None:
        logger.debug('waiting for messages')
        while True:
            try:
                msg_raw = await self.__msg_queue.get()
                msg = msg_raw.message
                logger.debug(f'executing "{msg.command}"{self.__registered_commands[msg.command.name]}')
                ctx, comm = self.__registered_commands[msg.command.name]
                comm(ctx, **{**msg.command.params, 'source_msg': msg})
                # self.__registered_commands[msg.command.name](self, **{**msg.command.params, 'source_msg': msg})
                self.__msg_queue.task_done()
            except asyncio.CancelledError:
                # logger.debug("fiiiiiiiiiiii")
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

    def commnads_register(self, comms: List[Tuple[Any, Type[Command]]]) -> None:
        for ctx_comm in comms:
            ctx, comm = ctx_comm
            logger.debug(f'registering "{comm.name}" commnad handler {comm.handler}')
            self.__registered_commands[comm.name] = (ctx, comm.handler) # type: ignore

    def command_send(self, addr: PeerAddr, comm: Command) -> None:
        logger.debug(f'sending commnad {comm}{type(comm)} to {addr}')
        self.msg_send(addr, Message(comm, self.addr))

    def commnad_send_bulk(self, comm: Command) -> None:
        logger.debug(f'sending {type(comm)} commnad {comm} to {self.__neighbors_addr}')
        m = Message(comm, self.addr)
        for addr in self.__neighbors_addr:
            self.msg_send(addr, m)

    # def commnad_direct(self, comm: Command) -> None:
    #     msg = Message(comm, self.addr)
    #     self.__msg_queue.put(RawMessage(msg.raw, self.addr))
