from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    price: Decimal
    created_at: datetime

class ProductUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)