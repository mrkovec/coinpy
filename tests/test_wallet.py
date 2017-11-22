import unittest

from coinpy.wallet import Wallet

class TestWalletMethods(unittest.TestCase):
    def setUp(self) -> None:
        self.wal = Wallet()

    def test_new_privkey(self) -> None:
        pass
        # self.wal.run_command()

if __name__ == '__main__':
    unittest.main()
