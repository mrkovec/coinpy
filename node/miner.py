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


def block_mine_internal(blk: Block) -> Block:
    logger.info(f'mining new block {blk}')
    while True:
        try:
            Rules.block_valid_difficulty(blk)
            return blk
        except Exception as e:
            pass
        blk.nonce += 1


class ExternalMiner(object):
    def __init__(self, loop: asyncio.AbstractEventLoop, addr: PeerAddr, new_blk_fnc) -> None:
        self.__io_loop = loop
        self.__addr = addr
        self.__mbq =  asyncio.Queue(1, loop = self.__io_loop)
        self.__new_blk_fnc = new_blk_fnc
        logger.info(f'Starting ExternalMiner {self.__addr}')
        self.__httpd = HTTPServer(self.__addr, external_miner_handler_factory(self.__io_loop, self.__mbq, self.__new_blk_fnc))

    async def block_mine(self) -> Block:
        while True:
            try:
                self.__io_loop.call_soon(self.__httpd.handle_request)
                return self.__mbq.get_nowait()
            except asyncio.QueueEmpty:
                await asyncio.sleep(1, loop=self.__io_loop)
            except KeyboardInterrupt:
                break
            except asyncio.CancelledError:
                break
        self.__httpd.server_close()
        logger.info('Stopping ExternalMiner')


def external_miner_handler_factory(loop, mbq, new_blk_fnc):
    class ExternalMinerHandler(BaseHTTPRequestHandler, object):
        def __init__(self, *args, **kwargs):
            self.__io_loop = loop
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
            self.__io_loop.run_until_complete(self.__mbq.put(Block.unserialize_json(post_data)))
            self._set_response(200)

    return ExternalMinerHandler
