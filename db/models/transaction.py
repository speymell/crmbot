from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base

if TYPE_CHECKING:
    from db.models.business import Business
    from db.models.finance_category import FinanceCategory
    from db.models.appointment import Appointment
    from db.models.user import User


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    business_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    type: Mapped[str] = mapped_column(String(16), nullable=False)  # income/expense

    category_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("finance_categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    appointment_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True, index=True
    )

    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    created_by_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    business: Mapped["Business"] = relationship(back_populates="transactions")
    category: Mapped["FinanceCategory | None"] = relationship(back_populates="transactions")
    appointment: Mapped["Appointment | None"] = relationship(back_populates="transactions")
    created_by_user: Mapped["User | None"] = relationship(back_populates="created_transactions")
