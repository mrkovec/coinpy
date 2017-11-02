import unittest
from coinpy.node.core import Node

class TestMining(unittest.TestCase):
    def test_node(self) -> None:
        nd = Node()
        self.assertIsInstance(nd, Node)
        self.assertIs(type(nd), Node)
