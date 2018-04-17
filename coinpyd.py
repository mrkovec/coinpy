from typing import Any
import argparse
import configparser
import logging
# import functools
import asyncio
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

from coinpy.node.node import Node
from coinpy.node.peer import PeerAddr
from coinpy.node.commands import GreetCommand
from coinpycli import CoinpyCLI

COINPYD_VERSION = '0.0.1'

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('asyncio').setLevel(logging.DEBUG)

class CoinpyDaemonRPCHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class CoinpyDaemonRPCServer(object):
    def __init__(self, loop: asyncio.AbstractEventLoop, node: Node, **config: Any) -> None:
        self.__io_loop = loop
        self.__node = node
        self.__RPCserver = None
        if 'rpcbind' in config:
            _, host, port = config['rpcbind']
            logger.info(f'starting rpc server {(host, port)}')
            self.__RPCserver = SimpleXMLRPCServer(
                    (host, port),
                    logRequests=True,
                    requestHandler=CoinpyDaemonRPCHandler)
            # rpc procedures
            def stop_daemon_cmd():
                self.__io_loop.call_soon_threadsafe(self.__node.stop_sync)
                return 'daemon stopped'
            self.__RPCserver.register_function(stop_daemon_cmd, 'stop')
            def addnode_daemon_cmd():
                return 'neighbor added'
            self.__RPCserver.register_function(addnode_daemon_cmd, 'addnode')

    def stop(self) -> None:
        if self.__RPCserver is not None:
            logger.info('stopping rpc server')
            self.__RPCserver.shutdown()
            self.__RPCserver.server_close()

    def run(self) -> None:
        if self.__RPCserver is not None:
            self.__io_loop.run_in_executor(None, self.__RPCserver.serve_forever)

class CoinpyDaemon(object):
    def __init__(self, args: Any) -> None:
        config = {}
        if args.addnode is not None:
            config['neighbors'] = [ PeerAddr((host, int(port))) for _, host, port in args.addnode ]
        config['gen'] = args.gen
        # config['gen_ext'] = args.genext
        if args.rpcbind is not None:
            config['rpcbind'] = args.rpcbind
        # node
        self.__io_loop = asyncio.get_event_loop()
        self.__io_loop.set_debug(True)
        _, host, port = args.bind
        self.__node = Node(self.__io_loop, addr=PeerAddr((host, port)), **config)
        self.__io_loop.run_until_complete(self.start())
        self.__tasks = [self.__io_loop.create_task(self.__node.msg_handle())]
        # rpc server
        self.__rpc.run()
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


    async def start(self) -> None:
        logger.debug('starting daemon')
        self.__rpc = CoinpyDaemonRPCServer(self.__io_loop, self, **self.__node.config)
        await self.__node.start()

    async def stop(self) -> None:
        logger.debug('stopping daemon')
        self.__rpc.stop()
        # cancel tasks
        for task in self.__tasks:
            task.cancel()
            await task
        await self.__node.stop()
        self.__io_loop.stop()

    def stop_sync(self) -> None:
        # for rpc
        self.__tasks.append(self.__io_loop.create_task(self.stop()))



def main() -> None:
    parser = argparse.ArgumentParser(prog='coinpyd', description=f'coinpy v{COINPYD_VERSION}')
    parser.add_argument('-bind', metavar='addr', required=True, type=CoinpyCLI.proc_addr, help='address in [host]:port form.')
    parser.add_argument('-rpcbind', metavar='addr', type=CoinpyCLI.proc_addr, help='address in [host]:port form.')
    parser.add_argument('-gen', action='store_true', default=False, help='Mine new blocks? Default %(default)s.')
    # parser.add_argument('-genext', action='store_true', default=False, help='Use external miner for mining? Default %(default)s.')
    parser.add_argument('-addnode', metavar='addr', type=CoinpyCLI.proc_addr, action='append', help='address in [host]:port form.')
    # parser_daemon.add_argument('-saveconf', action='store_true', default=False, help='Save settings into conf file? Default %(default)s.')
    parser.set_defaults(func=CoinpyDaemon)
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
