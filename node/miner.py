from typing import List
import multiprocessing
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import asyncio
# from time import time
# import sys

from coinpy.core.block import Block
from .peer import PeerAddr
from .consensus import Rules
logger = logging.getLogger(__name__)
# multiprocessing.log_to_stderr(logging.DEBUG)

class Miner(object):
    def __init__(self, blk: Block, mbq:  multiprocessing.Queue = None) -> None:
        self.__mbq = mbq
        self.__blk = blk

    def run(self) -> Block:
        while True:
            try:
                Rules.block_valid_difficulty(self.__blk)
                if self.__mbq is not None:
                    self.__mbq.put(self.__blk)
                return self.__blk
            except Exception as e:
                pass
            self.__blk.nonce += 1


class ExternalMiner(object):
    def __init__(self, loop: asyncio.AbstractEventLoop, addr: PeerAddr, mbq: multiprocessing.Queue, new_blk_fnc) -> None:
        self.__io_loop = loop
        self.__addr = addr
        self.__mbq = mbq
        self.__new_blk_fnc = new_blk_fnc

    async def run(self) -> None:
        httpd = HTTPServer(self.__addr, external_miner_handler_factory(self.__mbq, self.__new_blk_fnc))
        logger.info(f'Starting ExternalMiner {self.__addr}')
        while True:
            try:
                httpd.handle_request()
                await asyncio.sleep(0.1, loop=self.__io_loop)
            except KeyboardInterrupt:
                break
            except asyncio.CancelledError:
                break
        httpd.server_close()
        logger.info('Stopping ExternalMiner')


def external_miner_handler_factory(mbq: multiprocessing.Queue, new_blk_fnc):
    class ExternalMinerHandler(BaseHTTPRequestHandler, object):
        def __init__(self, *args, **kwargs):
            self.__mbq = mbq
            self.__block_assemble_new = new_blk_fnc
            super().__init__(*args, **kwargs)

        def _set_response(self, response_code: int) -> None:
            self.send_response(response_code)
            if response_code == 200:
                self.send_header('Content-type', 'application/json')
            self.end_headers()

        def do_GET(self) -> None:
            self._set_response(200)
            self.wfile.write(str(self.__block_assemble_new()).encode('utf-8'))

        def do_POST(self) -> None:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            self.__mbq.put(Block.unserialize_json(post_data))
            self._set_response(200)

    return ExternalMinerHandler
# class Scheduler(object):
#     def __init__(self, gen: List[Iterator[int]] = []) -> None:
#         self.active: List[Iterator[int]] = gen
#         self.scheduled: List[Iterator[int]] = []
#
#     def add_microthread(self, gen: Iterator[int]) -> None:
#         self.active.append(gen)
#
#     def run(self) -> Iterator[int]:
#         while True:
#             if len(self.active) == 0:
#                 return
#             for thread in self.active:
#                 try:
#                     next(thread)
#                     self.scheduled.append(thread)
#                 except StopIteration:
#                     pass
#                 yield 1
#             self.active, self.scheduled = self.scheduled, []
