from typing import List
from ecdsa import SigningKey, SECP256k1
import json
from base64 import b64encode, b64decode

class Wallet(object):
    def __init__(self) -> None:
        self.privkeys: List[str] = []
        #with  open('data.txt', 'w') as outfile:
        #     json.dump(data, outfile)
        try:
            self.load()
        except:
            pass

    def load(self) -> None:
        with open('wallet.json', 'r', encoding="utf-8") as infile:
            self.privkeys = json.load(infile)

    def save(self) -> None:
        with open('wallet.json', 'w', encoding="utf-8") as outfile:
            json.dump(self.privkeys, outfile)

    def new_privkey(self) -> None:
        self.privkeys.append(b64encode(SigningKey.generate(curve=SECP256k1).to_string()).decode())
        self.save()
