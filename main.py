from typing import Any
import argparse
import configparser
import logging
import functools
import asyncio
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc.client

from coinpy.node.node import Node
from coinpy.node.peer import PeerAddr
from coinpy.node.commands import GreetCommand

COINPY_VERSION = '0.0.1'

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('asyncio').setLevel(logging.DEBUG)

class CoinpyDaemonRPCHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)
    def cau(self):
        return 'cau'

class CoinpyDaemon(object):
    def __init__(self, args: Any) -> None:
        config = {}
        if args.addnode is not None:
            config['neighbors'] = [ PeerAddr((host, int(port))) for host, port in args.addnode ]
        config['gen'] = args.gen
        config['gen_ext'] = args.genext
        if args.rpc is not None:
            host, port = args.rpc
            config['rpc_addr'] = PeerAddr((host, int(port)))
        # node
        self.__io_loop = asyncio.get_event_loop()
        self.__io_loop.set_debug(True)

        self.__node = Node(self.__io_loop, addr=PeerAddr(tuple(args.bind)), **config)
        self.__io_loop.run_until_complete(self.start())
        self.__tasks = [self.__io_loop.create_task(self.__node.msg_handle())]
        # rpc server
        self.runRPC()
        # mining handler
        if config['gen']:
            self.__tasks.append(self.__io_loop.create_task(self.__node.block_mine_handle()))
        # greet neighbors
        self.__tasks.append(
                self.__io_loop.create_task(
                        self.__node.commnad_send_bulk(
                                GreetCommand(self.__node.last_block.height))))
        # run daemon
        completed, pending = self.__io_loop.run_until_complete(asyncio.wait(self.__tasks))


    def startRPC(self) -> None:
        if 'rpc_addr' in self.__node.config:
            addr = self.__node.config['rpc_addr']
            logger.debug(f'starting rpc server {addr}')
            self.__RPCserver = SimpleXMLRPCServer(
                    addr,
                    logRequests=True,
                    requestHandler=CoinpyDaemonRPCHandler)
            def stop_daemon():
                self.__io_loop.call_soon_threadsafe(self.stop_sync)
                return 'daemon stopped'
            self.__RPCserver.register_function(stop_daemon)

    def stopRPC(self) -> None:
        if 'rpc_addr' in self.__node.config:
            logger.debug('stopping rpc server')
            self.__RPCserver.shutdown()
            self.__RPCserver.server_close()

    def runRPC(self) -> None:
        if 'rpc_addr' in self.__node.config:
            self.__tasks.append(self.__io_loop.run_in_executor(None, self.__RPCserver.serve_forever))

    async def start(self) -> None:
        logger.debug('starting daemon')
        self.startRPC()
        await self.__node.start()

    async def stop(self) -> None:
        logger.debug('stopping daemon')
        self.stopRPC()
        # cancel tasks
        for task in self.__tasks:
            task.cancel()
            await task
        await self.__node.stop()
        self.__io_loop.stop()

    def stop_sync(self) -> None:
        self.__tasks.append(self.__io_loop.create_task(self.stop()))


class CoinpyCLI(object):
    def __init__(self, args: Any) -> None:
        host, port = args.stop
        with xmlrpc.client.ServerProxy(f'http://{host}:{port}/RPC2', verbose=True) as proxy:
            logger.debug(proxy.stop_daemon())


def main() -> None:
    parser = argparse.ArgumentParser(prog='coinpy', description=f'coinpy v{COINPY_VERSION}')
    subparsers = parser.add_subparsers(
            title='subcommands',
            # description='valid subcommands',
            help='runs %(prog)s in daemon or cli mode')
    parser_daemon = subparsers.add_parser('daemon')
    parser_daemon.add_argument('-bind', nargs=2, metavar=('host', 'port'), default=('127.0.0.1', 5001), help='The addres %(prog)s will listens on. Default %(default)s.')
    parser_daemon.add_argument('-gen', action='store_true', default=False, help='Mine new blocks? Default %(default)s.')
    parser_daemon.add_argument('-genext', action='store_true', default=False, help='Use external miner for mining? Default %(default)s.')
    parser_daemon.add_argument('-addnode', nargs=2, metavar=('host', 'port'), action='append', help='Neighbor peer to connect to.')
    parser_daemon.add_argument('-rpc', nargs=2, metavar=('host', 'port'))
    parser_daemon.add_argument('-saveconf', action='store_true', default=False, help='Save settings into conf file? Default %(default)s.')
    parser_daemon.set_defaults(func=CoinpyDaemon)
    parser_cli = subparsers.add_parser('cli')
    parser_cli.add_argument('-stop', nargs=2, metavar=('host', 'port'))
    parser_cli.set_defaults(func=CoinpyCLI)
    # logger.debug(parser.format_help())
    try:
        args = parser.parse_args()
        args.func(args)
    except Exception as e:
        parser.print_usage()
        logger.debug(str(e))



if __name__ == "__main__":
    main()
