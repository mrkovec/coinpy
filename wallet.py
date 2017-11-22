# import os
import logging
from typing import Dict, Callable, List

import pprint


from coinpy.core.crypto import Privkey, PrivkeyStorage


logger = logging.getLogger(__name__)

class Wallet(object):
    def __init__(self) -> None:
        self.__signing_keys = PrivkeyStorage.load_signing_keys()

        self.__commands: Dict[str, Callable[[List[str]], None]] = {
            'show-privkey': self.__show_signing_keys,
            'new-privkey': self.__new_signing_key
        }

    def __help(self, pars: List[str]) -> None:
        pass

    def __new_signing_key(self, pars: List[str]) -> None:
        if len(pars) == 0:
            raise Exception('enter privkey''s name')
        for sk_name in pars:
            sk = Privkey.new()
            PrivkeyStorage.store_signing_key(sk_name, sk)
            self.__signing_keys[sk_name] = sk

    def __show_signing_keys(self, pars: List[str]) -> None:
        if len(pars) == 0:
            pprint.pprint({ name: str(privkey.pubkey.pubaddr) for name, privkey in self.__signing_keys.items() })
        else:
            pprint.pprint({ name: str(self.__signing_keys[name].pubkey.pubaddr) for name in pars })

    def run_command(self, cmd: str = None) -> None:
        if cmd is None:
            cmd = input('--> ')
        cmd_pars = cmd.split()
        try:
            self.__commands[cmd_pars[0]](cmd_pars[1:])
            print('<-- OK')
        except Exception as e:
            print(f'<-- ERR {e}')
            raise e
