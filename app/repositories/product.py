from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product
from app.schemas.product import ProductUpdate

db_reads = 0


async def get_product_from_db(session: AsyncSession, product_id: int) -> Product | None:
    global db_reads
    db_reads += 1

    return await session.get(Product, product_id)

async def update_product_in_db(session: AsyncSession, product_id: int, data: ProductUpdate) -> Product | None:
    product = await session.get(Product, product_id)

    if product is None:
        return None

    product.name = data.name
    product.description = data.description
    product.price = data.price

    await session.commit()

    return product


