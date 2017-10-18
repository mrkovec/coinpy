import unittest
from .__setpaths__ import *

from coinpy.core.crypto import Hash, hash_from_str, hash_from_obj


class TestHashMethods(unittest.TestCase):
    def test_hash_from_str(self):
        self.assertEqual(hash_from_str('123').get_str(), 'xeDkbtzK6Y8gXoXVde+XuKnJ3ICVbUtkFZFHZQeI2jDEls0cNTCuqDMg1LcEcNtRFoUx26+ZZlKG6UMquoNEUw==')

    def test_hash_from_obj(self):
        self.assertEqual(hash_from_obj({'a': '123'}).get_str(), 'ECJWUv8efAIKb9sbtupyPi+/qJgwU4SBuajYbrMZ74pABzeT3km7zEB8HyLYurAu9aLMkDtqOoOYdrDfiFobwQ==')


if __name__ == '__main__':
    unittest.main()
