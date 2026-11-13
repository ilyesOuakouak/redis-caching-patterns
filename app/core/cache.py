from redis.asyncio import Redis
from app.core.config import settings

CACHE_TTL_SECONDS = 10 * 60

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


def get_redis() -> Redis:
    return redis_client


def product_cache_key(product_id: int) -> str:
    return f"product:{product_id}"
