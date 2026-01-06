from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base

if TYPE_CHECKING:
    from db.models.business import Business


class BusinessSetting(Base):
    __tablename__ = "business_settings"

    business_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("businesses.id", ondelete="CASCADE"), primary_key=True
    )

    booking_slot_minutes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="30")
    booking_horizon_days: Mapped[int] = mapped_column(Integer, nullable=False, server_default="30")

    allow_pending: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    reminder_24h: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    reminder_2h: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    business: Mapped["Business"] = relationship(back_populates="settings")
