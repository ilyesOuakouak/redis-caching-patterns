from fastapi import HTTPException, APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import Product
from app.schemas.product import ProductRead

INT_MAX = 2_147_483_647

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: int = Path(gt=0, le=INT_MAX),
    session: AsyncSession = Depends(get_session),
):
    product = await session.get(Product, product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product
