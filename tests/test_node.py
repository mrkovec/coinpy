import unittest
import time
from coinpy.node.node import Node, Scheduler
from coinpy.core.block import Block

class TestNode(unittest.TestCase):
    def setUp(self) -> None:
        self.nd = Node()
        # self.assertIsInstance(self.nd, Node)
        # self.assertIs(type(self.nd), Node)

    def test_mine(self) -> None:
        m = Scheduler([self.nd.mining_manager()])
        # for _ in m.run():
        #     pass


    # def test_sender_listener(self) -> None:
    #     lst = Listener()
    #     snd = Sender(b'aaa')
        # snd = Sender(b'bbb')
        # snd = Sender(b'cccc')
