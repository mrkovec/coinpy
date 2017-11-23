# import multiprocessing
import socket
import threading
import queue
import logging
import json
from typing import Iterator, List, Tuple, NewType, Dict, Callable, Any
from mypy_extensions import KwArg

# from coinpy.core import (
#     JsonDict, List, Tuple, NewType
# )
from coinpy.core import JsonDict
#
# from coinpy.core.transaction import Transaction
# from coinpy.core.block import Block
#
from coinpy.core.crypto import (
    Serializable
)
from coinpy.core.errors import (
    ValidationError
)
from .commands import (
    Command, GreetCommand
)


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


PEER_VERSION = 1


PeerAddr = NewType('PeerAddr', Tuple[str, int])


class Message(Serializable):
    def __init__(self, comm: Command, from_addr: PeerAddr, peer_ver: int = PEER_VERSION) -> None:
        self.ver = peer_ver
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


class InMessageWrap(object):
    def __init__(self, msg_raw: bytes, neighbor_addr: PeerAddr) -> None:
        self.__msg_json = msg_raw.decode('utf-8')
        self.__neighbor_addr = neighbor_addr

    @property
    def msg(self) -> Message:
        m = Message.unserialize_json(self.__msg_json)
        if m.ver != PEER_VERSION:
            raise ValidationError('incorrect msg version')
        if m.from_addr[0] != self.__neighbor_addr[0]:
            raise ValidationError('incorrect msg adrress')
        return m


class Peer(object):
    def __init__(self, addr: PeerAddr, comms: Dict[str, Callable[[KwArg(Any)], None]] = {}) -> None:
        self.addr = addr
        self.__msg_queue = queue.Queue() # type: ignore
        self.__neighbors_addr: List[PeerAddr] = []
        self.__registered_commands = {**comms}
        self.listen()

    def add_neighbor(self, n: PeerAddr) -> None:
        if n not in self.__neighbors_addr:
            self.__neighbors_addr.append(n)
            self.send_command(n, GreetCommand())

    def __lstn(self) -> None:
        while True:
            with socket.socket(socket.SOCK_DGRAM) as s:
                s.bind(self.addr)
                s.listen(5)
                conn, addr = s.accept()
                with conn:
                    msg_raw = b''
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        msg_raw += data
                    logger.debug(f'{self.addr} new msg {msg_raw}')
                    self.__msg_queue.put(InMessageWrap(msg_raw, addr))

    def listen(self) -> None:
        p =threading.Thread(target=self.__lstn, daemon=True)
        p.start()

    def send_command(self, addr: PeerAddr, comm: Command) -> None:
        self.send_msg(addr, Message(comm, self.addr))

    def send_msg(self, addr: PeerAddr, msg: Message) -> None:
        with socket.socket(socket.SOCK_DGRAM) as s:
            s.connect(addr)
            logger.debug(f'{self.addr} semding {msg}')
            s.sendall(str(msg).encode('utf-8'))

    def send_bulk_commnad(self, comm: Command) -> None:
        m = Message(comm, self.addr)
        for addr in self.__neighbors_addr:
            self.send_msg(addr, m)

    def direct_commnad(self, comm: Command) -> None:
        msg = Message(comm, self.addr)
        self.__msg_queue.put(InMessageWrap(str(msg).encode('utf-8'), self.addr))

    def process_msg(self) -> Iterator[int]:
        while True:
            try:
                m = self.__msg_queue.get_nowait()
                # logger.debug(f'working {m.msg}')
                self.__registered_commands[m.msg.command.name](**m.msg.command.kwargs)
            except queue.Empty:
                pass
            except Exception as e:
                logger.exception(str(e))
            yield 1

    # def __prcmsg(self, msg: MessageIn) -> None:
    #     msg_obj = msg.obj






# class Sender(object):
#     def __init__(self, data: bytes) -> None:
#         with socket.socket(socket.SOCK_DGRAM) as s:
#             logger.debug(f'send {data}')
#             s.connect(('127.0.0.1', 50007))
#             s.sendall(data)
#             # data = s.recv(1024)
#             # logger.debug(f'echo {data}')
#             # s.shutdown(socket.SHUT_RDWR)
#             # s.close()
#
# class Listener(object):
#     def __init__(self) -> None:
#         self.msg = b''
#         t = threading.Thread(target=self.run, daemon=True)
#         t.start()
#
#     def run(self) -> None:
#         while True:
#             with socket.socket( socket.SOCK_DGRAM) as s:
#                 # logger.debug(socket.gethostname())
#                 s.bind(('127.0.0.1', 50007))
#                 s.listen(5)
#                 conn, addr = s.accept()
#                 with conn:
#                     # logger.debug(f'Connected by {addr[0]}')
#                     self.msg = b''
#                     while True:
#                         data = conn.recv(2)
#                         if not data:
#                             break
#                         logger.debug(f'data {data}')
#                         self.msg += data
#                     logger.debug(f'rieceved {self.msg}')
#                     # conn.sendall(self.msg)
#
#                 # s.shutdown(socket.SHUT_RDWR)
#                 # s.close()
