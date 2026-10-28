from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base



class Statement(Base):

    __tablename__ = "statements"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False, 
    )

    file_hash: Mapped[str] = mapped_column(
        String(64), 
        unique=True, 
        nullable=False,
    )

    imported_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False,
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="statement",
        cascade="all, delete-orphan",
    )
