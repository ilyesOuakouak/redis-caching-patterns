import os
os.environ["DATABASE_URL"] = "postgresql+psycopg://app:app@localhost:5432/cache_demo_test"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"

from decimal import Decimal  # noqa: E402

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from redis.asyncio import Redis  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Product  # noqa: E402
from app.repositories import product as product_repo  # noqa: E402

assert "test" in settings.database_url, "Tests must never run against a non-test database"


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
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
    async with SessionLocal() as session:
        await session.execute(text("TRUNCATE product RESTART IDENTITY"))
        await session.commit()
    yield


@pytest.fixture
async def product():
    async with SessionLocal() as session:
        item = Product(name="Test keyboard", price=Decimal("49.90"), description="Fixture product")
        session.add(item)
        await session.commit()
    return item