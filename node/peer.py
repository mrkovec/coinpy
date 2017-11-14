# import multiprocessing
import socket
import threading
import queue
import logging
import json
from typing import Iterator, List, Tuple, NewType

# from coinpy.core import (
#     JsonDict, List, Tuple, NewType
# )
from coinpy.core.errors import (
    ValidationError
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

PEER_VERSION = 1

PeerAddr = NewType('PeerAddr', Tuple[str, int])

class Msg(object):
    def __init__(self, msg: object, from_addr: PeerAddr, peer_ver: int = PEER_VERSION) -> None:
        self.ver = peer_ver
        self.msg = msg
        self.from_addr = from_addr

    @property
    def raw(self) -> bytes:
        return json.dumps({'ver': self.ver, 'from': self.from_addr, 'msg': self.msg}).encode('utf-8')

    @classmethod
    def from_raw(cls, msg_bytes: bytes) -> 'Msg':
        dt = json.loads(msg_bytes)
        return cls(dt['msg'], dt['from'], dt['ver'])


class MsgIn(object):
    def __init__(self, msg_raw: bytes, neighbor_addr: PeerAddr) -> None:
        self.__msg_raw = msg_raw
        self.__neighbor_addr = neighbor_addr

    @property
    def obj(self) -> object:
        m = Msg.from_raw(self.__msg_raw)
        if m.ver != PEER_VERSION:
            raise ValidationError('incorrect msg version')
        if m.from_addr != self.__neighbor_addr:
            raise ValidationError('incorrect msg adrress')
        return m.msg


class Peer(object):
    def __init__(self, addr: PeerAddr) -> None:
        self.addr = addr
        self.__msg_queue = queue.Queue() # type: ignore
        self.__neighbors_addr: List[PeerAddr] = []
        self.listen()

    def add_neighbor(self, n: PeerAddr) -> None:
        if n not in self.__neighbors_addr:
            self.__neighbors_addr.append(n)

    def __lstn(self) -> None:
        while True:
            with socket.socket(socket.SOCK_DGRAM) as s:
                s.bind(self.addr)
                s.listen(5)
                conn, addr = s.accept()
                with conn:
                    msg = b''
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        msg += data
                    logger.debug(f'{self.addr} new msg {msg}')
                    self.__msg_queue.put(MsgIn(msg, addr))

    def listen(self) -> None:
        p =threading.Thread(target=self.__lstn, daemon=True)
        # p = multiprocessing.Process(target=self.lstn)
        p.start()


    def send_msg(self, msg: object) -> None:
        m = Msg(msg, self.addr)
        for addr in self.__neighbors_addr:
            with socket.socket(socket.SOCK_DGRAM) as s:
                s.connect(addr)
                logger.debug(f'{self.addr} semding {m}')
                s.sendall(m.raw)

    def process_msg(self) -> Iterator[int]:
        while True:
            try:
                self.__prcmsg(self.__msg_queue.get_nowait())
                # logger.debug(f'working {msg}')
            except queue.Empty:
                pass
            except Exception as e:
                logger.exception(str(e))
            yield 1

    def __prcmsg(self, msg: MsgIn) -> None:
        msg_obj = msg.obj






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
