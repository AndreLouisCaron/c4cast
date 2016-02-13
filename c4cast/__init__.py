# -*- coding: utf-8 -*-

import aiohttp.web
import argparse
import asyncio
import os.path
import pkg_resources
import signal
import sys

version = pkg_resources.resource_string('c4cast', 'version.txt')
version = version.decode('utf-8').strip()
"""Package version (as a dotted string)."""

here = os.path.dirname(os.path.abspath(__file__))

cli = argparse.ArgumentParser(description='Cash flow forecast.')
cli.add_argument('--version', action='version', version=version,
                 help="Print version and exit.")
cli.add_argument('--host', type=str, default='127.0.0.1',
                 action='store', dest='host',
                 help="IP address to bind to.")
cli.add_argument('--port', type=int, default=9000,
                 action='store', dest='port',
                 help="TCP port to bind to.")
cli.add_argument('--linger', type=float, default=1.0,
                 action='store', dest='linger',
                 help="Time to wait for TCP connections to close.")

async def _main(host, port, linger, cancel):
    loop = asyncio.get_event_loop()
    app = aiohttp.web.Application(loop=loop)
    app.router.add_static('/', os.path.join(here, 'assets'))
    handler = app.make_handler()
    server = await loop.create_server(handler, host, port)
    try:
        await cancel
    finally:
        server.close()
        await server.wait_closed()
        await handler.finish_connections(linger)
        await app.finish()

def main(arguments=None):
    if arguments is None:
        arguments = sys.argv[1:]
    arguments = cli.parse_args(arguments)
    loop = asyncio.get_event_loop()
    f = asyncio.Future()
    loop.add_signal_handler(signal.SIGINT, f.set_result, None)
    return loop.run_until_complete(_main(
        host=arguments.host,
        port=arguments.port,
        linger=arguments.port,
        cancel=f,
    ))
