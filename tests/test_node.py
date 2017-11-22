import unittest
import time
from coinpy.node.node import Node, Miner
from coinpy.core.block import Block

class TestNode(unittest.TestCase):
    def setUp(self) -> None:
        self.nd = Node()
        # self.assertIsInstance(self.nd, Node)
        # self.assertIs(type(self.nd), Node)

    def test_miner(self) -> None:
        blk_tmp = self.nd.assemble_block(self.nd.unprocessed_trxs)
        miner = Miner(blk_tmp)
        self.nd.add_block(miner.run())
        # blk_tmp = self.nd.assemble_block(self.nd.unprocessed_trxs)
        # miner = Miner(blk_tmp)
        # self.nd.add_block(miner.run())


        # m = Scheduler([self.nd.mining_manager()])
        # for _ in m.run():
        #     pass


    # def test_sender_listener(self) -> None:
    #     lst = Listener()
    #     snd = Sender(b'aaa')
        # snd = Sender(b'bbb')
        # snd = Sender(b'cccc')

if __name__ == '__main__':
    unittest.main()
