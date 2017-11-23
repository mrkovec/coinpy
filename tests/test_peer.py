import unittest
import time

from typing import Dict, Any


from coinpy.node.peer import Peer, PeerAddr, Command
from coinpy.node.node import Scheduler

class TestPeer(unittest.TestCase):
    def test_peer(self) -> None:
        p1 = Peer(PeerAddr(('127.0.0.1', 50001)),
            {'direct': command_new_trx}
        )
        p2 = Peer(PeerAddr(('127.0.0.1', 50002)))
        p1.add_neighbor(p2.addr)
        p1.direct_commnad(Command('direct', {'a':'1', 'b':2}))
        m = Scheduler([p2.process_msg(), p1.process_msg()])
        g = m.run()
        next(g)
        next(g)
        # next(g)
        # next(g)
        # for i in m.run():
        #     time.sleep(1)


def command_new_trx(**kwargs: Any) -> None:
    print(kwargs)
