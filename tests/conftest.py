# -*- coding: utf-8 -*-

import aiohttp
import pytest

@pytest.yield_fixture
def client(event_loop):
    session = aiohttp.ClientSession(loop=event_loop)
    try:
        yield session
    finally:
        session.close()
