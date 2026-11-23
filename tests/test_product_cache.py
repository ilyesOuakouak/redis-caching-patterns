import asyncio
import json

from sqlalchemy.util import await_

from app.core.cache import CACHE_TTL_SECONDS, product_cache_key
from app.repositories import product as product_repo


async def test_first_call_is_a_miss_and_fills_the_cache(client, redis, product):
    key = product_cache_key(product.id)

    response = await client.get(f"/products/{product.id}")

    assert response.status_code == 200
    assert product_repo.db_reads == 1

    cached = await redis.get(key)
    assert cached is not None
    assert json.loads(cached) == response.json()

    ttl = await redis.ttl(key)
    assert 0 < ttl <= CACHE_TTL_SECONDS


async def test_second_call_is_a_hit(client, product):
    response_1 = await client.get(f"/products/{product.id}")
    assert response_1.status_code == 200
    assert product_repo.db_reads == 1

    response_2 = await client.get(f"/products/{product.id}")

    assert response_2.status_code == 200
    assert product_repo.db_reads == 1
    assert response_2.json() == response_1.json()


async def test_expired_key_causes_a_new_miss_and_refills_cache(client, redis, product):
    key = product_cache_key(product.id)

    response_1 = await client.get(f"/products/{product.id}")
    assert response_1.status_code == 200
    assert product_repo.db_reads == 1

    await redis.pexpire(key, 100)  # 100 milliseconds
    await asyncio.sleep(0.2)  # wait past the expiry
    assert await redis.exists(key) == 0

    response_2 = await client.get(f"/products/{product.id}")

    assert response_2.status_code == 200
    assert product_repo.db_reads == 2
    assert await redis.exists(key) == 1

async def test_put_deletes_cache_key_and_next_get_returns_new_data(client, redis, product):
    key = product_cache_key(product.id)

    get_response_1 = await client.get(f"/products/{product.id}")
    assert get_response_1.status_code == 200

    assert await redis.exists(key) == 1

    product_data = {
        "name": "Claude Code Agent",
        "price": "79.90",
        "description": "Hi, this is the new update"
    }

    put_response = await client.put(f"/products/{product.id}", json=product_data)
    assert put_response.status_code == 200

    assert await redis.exists(key) == 0

    get_response_2 = await client.get(f"/products/{product.id}")

    assert get_response_2.status_code == 200

    second_content = get_response_2.json()

    assert await redis.exists(key) == 1

    assert second_content["name"] == product_data["name"]
    assert second_content["price"] == product_data["price"]
    assert second_content["description"] == product_data["description"]










