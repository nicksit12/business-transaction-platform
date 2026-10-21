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



class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    category_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="category"
    )

    default_merchants: Mapped[list["Merchant"]] = relationship(
        "Merchant",
        back_populates="default_category"

    )