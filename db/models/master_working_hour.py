from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, ForeignKey, SmallInteger, Time, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from db.models.business import Business
    from db.models.master import Master


class MasterWorkingHour(Base):
    __tablename__ = "master_working_hours"
    __table_args__ = (
        UniqueConstraint("master_id", "weekday", name="uq_master_working_hours_master_weekday"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    business_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    master_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("masters.id", ondelete="CASCADE"), nullable=False, index=True
    )

    weekday: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 0..6 or 1..7

    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    break_start: Mapped[time | None] = mapped_column(Time, nullable=True)
    break_end: Mapped[time | None] = mapped_column(Time, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    business: Mapped["Business"] = relationship(back_populates="master_working_hours")
    master: Mapped["Master"] = relationship(back_populates="working_hours")
