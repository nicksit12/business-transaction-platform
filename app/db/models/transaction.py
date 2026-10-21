from __future__ import annotations

from datetime import date, datetime 
from decimal import Decimal



from sqlalchemy import(
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

class Transaction(Base):
    __tablename__ = "transactions"

    __table_args__ = (
        UniqueConstraint(
            "statement_id", 
            "source_row_number",
            name = "uq_statement_source_row",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    statement_id: Mapped[int] = mapped_column(
        ForeignKey("statements.id"),
        nullable=False,
    )

    source_row_number: Mapped[int] = mapped_column(
        nullable=False
    )

    transaction_date: Mapped[date] = mapped_column(
        Date, 
        nullable=False, 
        index=True 
    )

    description: Mapped[str] = mapped_column(
        String(500), 
        nullable=False
    )

    normalized_description: Mapped[str] = mapped_column(
        String(500), 
        nullable=False, 
        index=True, 
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    merchant_id: Mapped[int | None] = mapped_column(
        ForeignKey("merchants.id"), 
        nullable=True,
    )

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True,
    )

    classification_status: Mapped[str] = mapped_column(
        String(30),
        default="unclassified",
        nullable=False,
    )

    classification_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )


    statement: Mapped["Statement"] = relationship(
        "Statement",
        back_populates="transactions"
    )

    merchant: Mapped["Merchant | None"] = relationship(
        "Merchant",
        back_populates="transactions"
    )

    category: Mapped["Category | None"] = relationship(
        "Category",
        back_populates="transactions"
    )

