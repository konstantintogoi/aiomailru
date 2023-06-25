import asyncio
import json
from typing import Generator

import pytest

from aiomailru.sessions import PublicSession


@pytest.fixture(scope='session')
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Event loop."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def error():
    return {'error': {'error_code': -1, 'error_msg': 'test error msg'}}


@pytest.fixture
def data():
    return {'key': 'value'}


@pytest.yield_fixture
async def error_server(httpserver, error):
    httpserver.serve_content(**{
        'code': 401,
        'headers': {'Content-Type': PublicSession.CONTENT_TYPE},
        'content': json.dumps(error),
    })
    return httpserver


@pytest.yield_fixture
async def data_server(httpserver, data):
    httpserver.serve_content(**{
        'code': 200,
        'headers': {'Content-Type': PublicSession.CONTENT_TYPE},
        'content': json.dumps(data),
    })
    return httpserver
