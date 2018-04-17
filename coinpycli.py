from typing import Any,Tuple
import xmlrpc.client
import logging
import argparse
from urllib.parse import urlparse, urlsplit, urljoin, ParseResult
import functools

COINPYCLI_VERSION = '0.0.1'

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class CoinpyCLI(object):
    @staticmethod
    def proc_addr(addr: str) -> Tuple[str, str, int]:
        p = urlparse(addr, 'http')
        netloc = p.netloc or p.path
        if netloc.startswith(':'):
            netloc = 'localhost' + netloc
        path = p.path if p.netloc else ''
        p = ParseResult('http', netloc, path, '', '', '')
        return (p.geturl(), p.hostname, p.port)

    @staticmethod
    def stop_cmd(args: Any) -> None:
        addr, _, _ = args.addr
        with xmlrpc.client.ServerProxy(addr, verbose=True) as proxy:
            logger.debug(proxy.stop())

def main() -> None:
    parser = argparse.ArgumentParser(prog='coinpycli', description=f'%(prog)s v{COINPYCLI_VERSION}')
    # parser.add_argument('--verbose', '-v', action='count')
    subparsers = parser.add_subparsers(title='commands', description='valid %(prog)s commands')
    parser_stop = subparsers.add_parser('stop')
    parser_stop.add_argument('addr', type=CoinpyCLI.proc_addr, help='coinpyd rpc address in [host]:port form.')
    parser_stop.set_defaults(func=CoinpyCLI.stop_cmd)

    parser_addnode = subparsers.add_parser('addnode')
    parser_addnode.add_argument('addr', type=CoinpyCLI.proc_addr)
    parser_addnode.set_defaults(func=CoinpyCLI)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        logger.exception(str(e))

if __name__ == "__main__":
    main()
