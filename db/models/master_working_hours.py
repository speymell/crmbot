from __future__ import annotations

from datetime import datetime, time

from sqlalchemy import BigInteger, ForeignKey, SmallInteger, DateTime, Boolean, text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from db.models.businesses import Business
    from db.models.masters import Master


class MasterWorkingHours(Base):
    __tablename__ = "master_working_hours"
    __table_args__ = (
        UniqueConstraint("master_id", "weekday", name="uq_master_weekday"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    business_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    master_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("masters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    weekday: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    break_start: Mapped[time | None] = mapped_column(Time, nullable=True)
    break_end: Mapped[time | None] = mapped_column(Time, nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    business: Mapped["Business"] = relationship(back_populates="master_working_hours")
    master: Mapped["Master"] = relationship(back_populates="master_working_hours")