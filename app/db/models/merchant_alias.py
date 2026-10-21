

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base



class MerchantAlias(Base):
    __tablename__ = "merchant_aliases"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    merchant_id: Mapped[int] = mapped_column(
        ForeignKey("merchants.id"),
        nullable=False,
    )

    normalized_alias: Mapped[str] = mapped_column(
        String(300),
        unique=True,
        nullable=False,
        index=True,
    )

    merchant: Mapped["Merchant"] = relationship(
        "Merchant",
        back_populates="aliases"
    )