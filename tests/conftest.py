import os

os.environ["REDIS_URL"] = "redis://localhost:6379/1"

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis

from app.core.config import settings
from app.main import app
from app.repositories import product as product_repo


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def redis():
    client = Redis.from_url(settings.redis_url, decode_responses=True)
    yield client
    await client.aclose()


@pytest.fixture(autouse=True)
async def clean_state(redis):
    product_repo.db_reads = 0
    await redis.flushdb()
    yield

