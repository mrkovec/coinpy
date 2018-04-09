import logging
from behave.api.async_step import use_or_create_async_context, AsyncContext

def before_all(context):
    if not context.config.log_capture:
        logging.basicConfig(level=logging.DEBUG)

def before_scenario(context, scenario):
    context.async_loop = use_or_create_async_context(context, "async_context1").loop
    context.port_seq = 5000
    context.node = {}
    context.block_new = {}
