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

from base import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    canonical_name: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
    )

    default_category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True,
    )


    default_category: Mapped["Category | None"] = relationship(
        "Category",
        back_populates="default_merchants"
    )

    aliases: Mapped[list["MerchantAlias"]] = relationship(
        "MerchantAlias",
        back_populates="merchant",
        cascade="all, delete-orphan",
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="merchant"
    )