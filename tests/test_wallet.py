import unittest

from .__setpaths__ import *
from coinpy.core.wallet import Wallet

class TestWalletMethods(unittest.TestCase):
    def setUp(self):
        self.wal = Wallet()

    def test_new_privkey(self):
        print(self.wal.new_privkey())

if __name__ == '__main__':
    unittest.main()
