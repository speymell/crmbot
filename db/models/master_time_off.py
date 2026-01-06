from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base

if TYPE_CHECKING:
    from db.models.business import Business
    from db.models.master import Master


class MasterTimeOff(Base):
    __tablename__ = "master_time_off"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    business_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    master_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("masters.id", ondelete="CASCADE"), nullable=False, index=True
    )

    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    business: Mapped["Business"] = relationship(back_populates="master_time_off")
    master: Mapped["Master"] = relationship(back_populates="time_off")
