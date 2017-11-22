import unittest
import time

from coinpy.node.peer import Peer, PeerAddr
from coinpy.node.node import Scheduler

# class TestPeer(unittest.TestCase):
#     def test_peer(self) -> None:
#         p1 = Peer(PeerAddr(('127.0.0.1', 50001)))
#         p2 = Peer(PeerAddr(('127.0.0.1', 50002)))
        # p3 = Peer(PeerAddr(('127.0.0.1', 50003)))
        # p1.add_neighbor(p2.addr)
        # p1.add_neighbor(p3.addr)
        # p1.send_msg({'text':'hooo'})
        # time.sleep(1)
        # g = p1.test_gen()

        # m = Scheduler([p2.process_msg()])
        # m.add_microthread(p2.test_gen())
        # for i in m.run():
        #     print(i)
        #     time.sleep(1)
