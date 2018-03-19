import unittest
import time
import threading
import logging
import asyncio
import sys
from typing import Dict, Any

from io import StringIO
from unittest.mock import patch

# from coinpy.node.peer import Peer, PeerAddr

# from coinpy.node.commands import Command

# from coinpy.node.node import Scheduler

from coinpy.node.commands import Command
from coinpy.node.peer import (
    Peer, PeerAddr
)

logging.basicConfig(level=logging.DEBUG)

class TestPeer(unittest.TestCase):
    def setUp(self) -> None:

        self.p1_loop = asyncio.new_event_loop()
        self.p2_loop = asyncio.new_event_loop()
        # self.p1_loop.set_debug(True)
        # self.p2_loop.set_debug(True)
        self.p1 = Peer(PeerAddr(('127.0.0.1', 50001)), self.p1_loop)
        self.p2 = Peer(PeerAddr(('127.0.0.1', 50002)), self.p2_loop)
        self.p1.neighbors_add([self.p2.addr])
        self.p2.neighbors_add([self.p1.addr])

    def tearDown(self) -> None:
        self.p1.stop()
        self.p2.stop()
        self.p1_loop.stop()
        self.p2_loop.stop()

    def test_peer_pingpong_msg(self) -> None:
        self.p1.commnads_register([(self.p1, PongCommand)])
        self.p2.commnads_register([(self.p2, PingCommand)])
        self.p1.commnad_send_bulk(PingCommand())
        threading.Thread(target=lambda: self.p1_loop.run_forever(), daemon=True).start()
        threading.Thread(target=lambda: self.p2_loop.run_forever(), daemon=True).start()
        with patch('sys.stdout', new=StringIO()) as fo:
            time.sleep(0.1)
            self.assertEqual(fo.getvalue().strip(), "ping from ['127.0.0.1', 50001]\npong from ['127.0.0.1', 50002]")



class PingCommand(Command):
    name = 'ping'
    @staticmethod
    def handler(ctx: Any, **kwargs:Any) -> None:
        print(f'{PingCommand.name} from {kwargs["source_msg"].from_addr}')
        sys.stdout.flush()
        ctx.commnad_send_bulk(PongCommand())

class PongCommand(Command):
    name = 'pong'
    @staticmethod
    def handler(ctx: Any, **kwargs:Any) -> None:
        print(f'{PongCommand.name} from {kwargs["source_msg"].from_addr}')
        sys.stdout.flush()
