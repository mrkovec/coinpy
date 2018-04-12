from typing import Any
import argparse
import configparser
import logging
import functools
import asyncio

from coinpy.node.node import Node
from coinpy.node.peer import PeerAddr
from coinpy.node.commands import GreetCommand

COINPY_VERSION = '0.0.1'

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

class CoinpyDaemon(object):
    def __init__(self, args: Any) -> None:
        config = {}
        if args.addnode is not None:
            config['neighbors'] = [ PeerAddr((host, int(port))) for host, port in args.addnode ]
        config['gen'] = args.gen
        config['gen_ext'] = args.genext
        self.__io_loop = asyncio.get_event_loop()
        self.__node = Node(self.__io_loop, addr=PeerAddr(args.bind), **config)

        self.__io_loop.run_until_complete(self.start())
        self.__tasks = [self.__io_loop.create_task(self.__node.msg_handle())]
        if config['gen']:
            self.__tasks.append(self.__io_loop.create_task(self.__node.block_mine_handle()))

        self.__tasks.append(self.__io_loop.create_task(self.__node.commnad_send_bulk(GreetCommand(self.__node.last_block.height))))

        self.__io_loop.run_until_complete(asyncio.wait(self.__tasks))

    async def start(self) -> None:
        await self.__node.start()

    async def stop(self) -> None:
        # cancel tasks
        for task in self.__tasks:
            task.cancel()
            await task
        await self.__node.stop()


class CoinpyCLI(object):
    pass

def main() -> None:
    parser = argparse.ArgumentParser(prog='coinpy', description=f'coinpy v{COINPY_VERSION}')
    subparsers = parser.add_subparsers(
            title='subcommands',
            # description='valid subcommands',
            help='runs %(prog)s in daemon or cli mode')
    parser_daemon = subparsers.add_parser('daemon')
    parser_daemon.add_argument('--bind', nargs=2, metavar=('host', 'port'), default=('127.0.0.1', 5003), help='The addres %(prog)s will listens on. Default %(default)s.')
    parser_daemon.add_argument('--gen', action='store_true', default=False, help='Mine new blocks? Default %(default)s.')
    parser_daemon.add_argument('--genext', action='store_true', default=False, help='Use external miner for mining? Default %(default)s.')
    parser_daemon.add_argument('--addnode', nargs=2, metavar=('host', 'port'), action='append', help='Neighbor peer to connect to.')
    parser_daemon.add_argument('--saveconf', action='store_true', default=False, help='Save settings into conf file? Default %(default)s.')
    parser_daemon.set_defaults(func=CoinpyDaemon)
    # parser_cli = subparsers.add_parser('cli')
    # parser_cli.add_argument('z')
    # parser_daemon.set_defaults(func=CoinpyCLI)
    # logger.debug(parser.format_help())
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
