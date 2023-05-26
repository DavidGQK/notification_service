import asyncio

import aiohttp
import aioredis
import pytest
from aioredis import Redis

from tests.functional.settings import test_settings as TS


@pytest.fixture(scope='session')
def event_loop():
    """
    Creates an event loop instance, by default, for each test case.
    https://pypi.org/project/pytest-asyncio/#:~:text=event_loop():
    """
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def redis_client():
    redis: Redis = await aioredis.from_url(
        f'redis://{TS.redis_host_t}:{TS.redis_port_t}',
        decode_responses=True, max_connections=20)
    yield redis
    await redis.flushall()
    await redis.close()


@pytest.fixture(scope='session')
async def session() -> aiohttp.ClientSession:
    session = aiohttp.ClientSession()
    yield session
    await session.close()
