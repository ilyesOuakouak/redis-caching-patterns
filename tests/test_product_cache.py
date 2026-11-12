import json

from app.core.cache import CACHE_TTL_SECONDS
from app.repositories import product as product_repo

async def test_first_call_is_a_miss_and_fills_the_cache(client, redis):
    response = await client.get("/products/1")

    assert response.status_code == 200
    assert product_repo.db_reads == 1

    cached = await redis.get("product:1")
    assert cached is not None
    assert json.loads(cached) == response.json()

    ttl = await redis.ttl("product:1")
    assert 0 < ttl <= CACHE_TTL_SECONDS


async def test_second_call_is_a_hit(client):
    response_1 = await client.get("/products/1")

    assert response_1.status_code == 200
    assert product_repo.db_reads == 1

    response_2 = await client.get("/products/1")
    assert response_2.status_code == 200
    assert product_repo.db_reads == 1

    assert response_2.json() == response_1.json()