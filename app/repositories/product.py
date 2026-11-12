from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product

db_reads = 0



async def get_product_from_db(session: AsyncSession, product_id: int) -> Product | None:
    global db_reads
    db_reads += 1

    return await session.get(Product, product_id)
