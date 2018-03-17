import unittest
import time
import logging
import asyncio
import threading

from coinpy.node.node import Node, Miner
from coinpy.core.block import Block
from coinpy.node.peer import Peer, PeerAddr

logging.basicConfig(level=logging.DEBUG)

# class TestNodeTrx(unittest.TestCase):
#     def setUp(self) -> None:
#         asyncio.set_event_loop(None)
#         self.loop1 = asyncio.new_event_loop()
#         self.loop2 = asyncio.new_event_loop()
#         # self.loop1.set_debug(True)
#         # self.loop2.set_debug(True)
#         self.n1 = Node(self.loop1, addr=PeerAddr(('127.0.0.1', 50001)), neighbors=[('127.0.0.1', 50002)])
#         self.n2 = Node(self.loop2, addr=PeerAddr(('127.0.0.1', 50002)))

# class TestNode(unittest.TestCase):
#     def setUp(self) -> None:
#         asyncio.set_event_loop(None)
#         self.loop = asyncio.new_event_loop()
#         self.nd = Node(self.loop)
#
#     def tearDown(self) -> None:
#         self.nd.stop()
#         pending = asyncio.Task.all_tasks(loop=self.loop)
#         for task in pending:
#             task.cancel()
#         try:
#             self.loop.run_until_complete(asyncio.gather(*pending))
#         except asyncio.CancelledError: # Any other exception would be bad
#             pass
#             # logging.debug("Cancelled %s: %s", task, task.cancelled())
#         self.loop.stop()
#
#     def test_miner(self) -> None:
#         blk_tmp = self.nd.assemble_new_block(self.nd.unprocessed_transactions)
#         miner = Miner(blk_tmp)
#         self.nd.add_block(miner.run())


class TestNodePeer(unittest.TestCase):
    def setUp(self) -> None:
        asyncio.set_event_loop(None)
        self.loop1 = asyncio.new_event_loop()
        self.loop2 = asyncio.new_event_loop()
        # self.loop1.set_debug(True)
        # self.loop2.set_debug(True)
        self.n1 = Node(self.loop1, addr=PeerAddr(('127.0.0.1', 50001)), neighbors=[('127.0.0.1', 50002)])
        self.n2 = Node(self.loop2, addr=PeerAddr(('127.0.0.1', 50002)))

    def test_async_mining(self) -> None:
        asyncio.ensure_future(self.n1.mine_block(), loop=self.loop1)
        # self.loop1.run_forever()
        threading.Thread(target=lambda: self.loop1.run_forever(), daemon=True).start()
        threading.Thread(target=lambda: self.loop2.run_forever(), daemon=True).start()
        time.sleep(5)


    # def tearDown(self) -> None:
        # self.n1.stop()
        # self.n2.stop()
        # self.loop1.stop()
        # self.loop2.stop()

    # def test_async_mining(self) -> None:
        # # logging.debug('1')
        # # pending = asyncio.Task.all_tasks(loop=self.loop1)
        # # for task in pending:
        # #     logging.debug(f'pending {task}')
        # # logging.debug('2')
        # # pending = asyncio.Task.all_tasks(loop=self.loop2)
        # # for task in pending:
        # #     logging.debug(f'pending {task}')
        #
        # # self.loop1.run_forever()
        # self.loop1.create_task(self.n1.mine_block())
        # threading.Thread(target=lambda: self.loop2.run_forever(), daemon=True).start()
        # threading.Thread(target=lambda: self.loop1.run_forever(), daemon=True).start()
        # # threading.Thread(target=lambda: self.loop1.run_until_complete(self.n1.mine_block()), daemon=True).start()
        # # self.loop1.run_until_complete(self.n1.mine_block())
        # time.sleep(5)



if __name__ == '__main__':
    unittest.main()
