from behave import given, when, then, step
from behave.api.async_step import use_or_create_async_context, AsyncContext
import asyncio


from coinpy.node.node import Node
from coinpy.core.block import Block
from coinpy.node.peer import PeerAddr
from coinpy.node.commands import AnnounceBlockCommand



@step('node "{node_name}" receives new block')
def step_node_receive_block(context, node_name):
    async_context = use_or_create_async_context(context, "async_context1")
    node = context.node[node_name]
    receive_task = async_context.loop.create_task(node.command_receive())
    command = async_context.loop.run_until_complete(receive_task)
    assert receive_task.done() is True
    context.block_new[node_name] = Block.unserialize(command.params['blk'])

@step('node "{node_name}" announces new block to node "{neighbor_node_name}"')
def step_node_announce_block(context, node_name, neighbor_node_name):
    async_context = use_or_create_async_context(context, "async_context1")
    node = context.node[node_name]
    neighbor_addr = context.node[neighbor_node_name].addr
    send_task = async_context.loop.create_task(node.command_send(neighbor_addr, AnnounceBlockCommand(context.block_new[node_name])))
    async_context.loop.run_until_complete(send_task)
    assert send_task.done() is True

@step('node "{neighbor_node_name}" is neighbor of node "{node_name}"')
def step_node_add_neighbor(context, neighbor_node_name, node_name):
    context.node[node_name].neighbors_add(context.node[neighbor_node_name].addr)

@step('we have running node "{node_name}" on port "{port:d}"')
def step_node_start_addr(context, node_name, port):
    async_context = use_or_create_async_context(context, "async_context1")
    context.node[node_name] = Node(async_context.loop, addr=PeerAddr(('127.0.0.1', port)))
    start_task = async_context.loop.create_task(context.node[node_name].start())
    # async_context.tasks.append(start_t)
    async_context.loop.run_until_complete(start_task)
    # async_context.loop.run_until_complete(context.node[node_name].start())
    assert start_task.done() is True

@step('node "{node_name}" mines new block')
def step_node_mine_block(context, node_name):
    async_context = context.async_context1
    # done, pending = async_context.loop.run_until_complete(asyncio.wait([context.node.block_await()]))
    # done, pending = async_context.loop.run_until_complete(asyncio.wait([context.node[node_name].block_mine()]))
    mine_task = async_context.loop.create_task(context.node[node_name].block_mine())
    context.block_new[node_name] = async_context.loop.run_until_complete(mine_task)
    assert mine_task.done() is True

@step('node "{node_name}" validates new block')
def step_node_mine_block(context, node_name):
    context.node[node_name].block_validate(context.block_new[node_name])

@step('node "{node_name}" adds new block to his blockchain')
def step_node_store_block(context, node_name):
    context.node[node_name].block_add_to_blockchain(context.block_new[node_name])
    assert context.node[node_name].blockchain_height == 1

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
