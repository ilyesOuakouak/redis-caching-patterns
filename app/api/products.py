from fastapi import HTTPException, APIRouter, Depends, Path
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.cache import get_redis, product_cache_key, CACHE_TTL_SECONDS
from app.repositories.product import get_product_from_db
from app.schemas.product import ProductRead

INT_MAX = 2_147_483_647

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: int = Path(gt=0, le=INT_MAX),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    key = product_cache_key(product_id)
    cached = await redis.get(key)

    if cached is not None:
        return ProductRead.model_validate_json(cached)

    product = await get_product_from_db(session, product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product_read = ProductRead.model_validate(product)

    await redis.set(key, product_read.model_dump_json(), ex=CACHE_TTL_SECONDS)

    return product_read
