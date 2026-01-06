from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base

if TYPE_CHECKING:
    from db.models.business import Business
    from db.models.master import Master
    from db.models.appointment import Appointment
    from db.models.transaction import Transaction


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("business_id", "tg_user_id", name="uq_users_business_tg"),
        UniqueConstraint("business_id", "email", name="uq_users_business_email"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    business_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    role: Mapped[str] = mapped_column(String(16), nullable=False, server_default=text("'master'"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    tg_user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    business: Mapped["Business"] = relationship(back_populates="users")
    master_profile: Mapped["Master | None"] = relationship(back_populates="user", uselist=False)

    created_appointments: Mapped[list["Appointment"]] = relationship(back_populates="created_by_user")
    created_transactions: Mapped[list["Transaction"]] = relationship(back_populates="created_by_user")
