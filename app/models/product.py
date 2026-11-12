from decimal import Decimal
from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, func, Numeric
from sqlalchemy.orm import Mapped, mapped_column


from app.core.database import Base


class Product(Base):
    __tablename__ = "product"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
