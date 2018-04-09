from behave import given, when, then, step
from behave.api.async_step import use_or_create_async_context, AsyncContext
import asyncio
import os

from coinpy.node.node import Node
from coinpy.core.block import Block
from coinpy.node.peer import PeerAddr
from coinpy.node.commands import AnnounceBlockCommand, GreetCommand, InfoCommand
from coinpy.node.miner import ExternalMiner

@step('node "{node_name}" receives "{message}" message from node "{neighbor_node_name}"')
def step_node_receive_message(context, node_name, message, neighbor_node_name):
    receive_task = context.async_loop.create_task(
            context.node[node_name].msg_receive())
    msg = context.async_loop.run_until_complete(receive_task)
    assert receive_task.done() is True
    assert msg.command.name == message
    assert msg.from_addr == list(context.node[neighbor_node_name].addr)
    if message == AnnounceBlockCommand.name:
        context.block_new[node_name] = Block.unserialize(msg.command.params['blk'])


@step('node "{node_name}" sends "{message}" message to node "{neighbor_node_name}"')
def step_node_send_message(context, node_name, message, neighbor_node_name):
    def form_command(message):
        if message == GreetCommand.name:
            return GreetCommand(context.node[node_name].last_block.height)
        if message == InfoCommand.name:
            return InfoCommand(context.node[node_name].last_block.height)
        if message == AnnounceBlockCommand.name:
            return AnnounceBlockCommand(context.block_new[node_name])

    send_task = context.async_loop.create_task(
            context.node[node_name].command_send(
                    context.node[neighbor_node_name].addr,
                    form_command(message)))
    context.async_loop.run_until_complete(send_task)
    assert send_task.done() is True


@step('node "{neighbor_node_name}" is neighbor of node "{node_name}"')
def step_node_add_neighbor(context, neighbor_node_name, node_name):
    context.node[node_name].neighbors_add([context.node[neighbor_node_name].addr])


@step('we have running node "{node_name}"')
def step_node_start(context, node_name):
    context.port_seq += 1
    context.node[node_name] = Node(
            context.async_loop,
            addr=PeerAddr(('127.0.0.1', context.port_seq)))
    start_task = context.async_loop.create_task(context.node[node_name].start())
    context.async_loop.run_until_complete(start_task)
    assert start_task.done() is True


@step('node "{node_name}" stops')
def step_node_stop(context, node_name):
    stop_task = context.async_loop.create_task(context.node[node_name].stop())
    context.async_loop.run_until_complete(stop_task)
    assert stop_task.done() is True


@step('node "{node_name}" mines new block')
def step_node_mine_block(context, node_name):
    mine_task = context.async_loop.create_task(
            context.node[node_name].block_mine())
    context.block_new[node_name] = context.async_loop.run_until_complete(mine_task)
    assert mine_task.done() is True


@step('node "{node_name}" validates new block')
def step_node_mine_block(context, node_name):
    context.node[node_name].block_validate(context.block_new[node_name])


@step('node "{node_name}" adds new block to his blockchain')
def step_node_store_block(context, node_name):
    context.node[node_name].block_add_to_blockchain(context.block_new[node_name])
    assert context.node[node_name].last_block.height == 1

@step('node "{node_name}" listens for external mined block')
def step_node_listen_external_miner(context, node_name):
    context.node[node_name].external_miner_start(PeerAddr(('127.0.0.1', 2020)))
    # context.ext_miner = ExternalMiner(
    #         context.async_loop, addr,
    #         context.node[node_name].block_assemble_new_full)
    # mine_task = context.async_loop.create_task(
    #         context.node[node_name].block_mine_external(addr))
    # context.block_new[node_name] = context.async_loop.run_until_complete(mine_task)
    # assert mine_task.done() is True

    #
@step('we have running "{miner_executable}"')
def step_external_miner_run(context, miner_executable):
    # subprocess.call(miner_executable, shell=True)
    os.startfile(miner_executable)

@step('external miner sends new block to node "{node_name}"')
def step_node_mine_block(context, node_name):
    mine_task = context.async_loop.create_task(
            context.node[node_name].block_mine_external())
    context.block_new[node_name] = context.async_loop.run_until_complete(mine_task)
    assert mine_task.done() is True

    # os.system(miner_executable)
# @when('node mines new block')
# def step_node_mine(context):
#      context.execute_steps('When node "A" mines new block')
#
# @given('we have mining node running')
# def step_node_start(context):
#      context.execute_steps('Given we have running node "A" on port "5011"')
#
# @then('block will match the consensus rules')
# def step_node_block_validate(context):
#     context.execute_steps('Then node "A" validates new block')
