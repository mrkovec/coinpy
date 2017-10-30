import sys
import os

PACKAGE_PARENT = os.path.join('..','..')
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from coinpy.core.crypto import Pubkey

TEST_PUBKEY = Pubkey(b'P3\n\x17k\xf4\x97\x8a\xa5\x13S{\xe9\x138o\x12v\xf8jb\x86\xe4\xc2\xcei\xd2\xdd\x082\xe5`\xab\xb2"w\xc6\x93w\xf2\xb9\xdc(\x0f\xd8\xa7\xc6t\xd7\'\xa6\x92\xa1\x1do\xb9\x89(\xd9pDj\xf4\xa2')
TEST_PUBADDR = TEST_PUBKEY.pubaddr

PEM_FILE_DATA = '''-----BEGIN EC PRIVATE KEY-----
MHQCAQEEIM0QyN9/lLMDTGaCeWZqZO1T5e8BR3PS708FXyyJGhfJoAcGBSuBBAAK
oUQDQgAEUDMKF2v0l4qlE1N76RM4bxJ2+GpihuTCzmnS3Qgy5WCrsiJ3xpN38rnc
KA/Yp8Z01yemkqEdb7mJKNlwRGr0og==
-----END EC PRIVATE KEY-----'''
