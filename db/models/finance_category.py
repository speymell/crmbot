from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from db.models.business import Business
    from db.models.transaction import Transaction


class FinanceCategory(Base):
    __tablename__ = "finance_categories"
    __table_args__ = (
        UniqueConstraint("business_id", "name", "type", name="uq_finance_categories_business_name_type"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    business_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(16), nullable=False)  # income/expense

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    business: Mapped["Business"] = relationship(back_populates="finance_categories")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="category")
