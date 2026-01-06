from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base

if TYPE_CHECKING:
    from db.models.business import Business
    from db.models.client import Client
    from db.models.master import Master
    from db.models.service import Service
    from db.models.user import User
    from db.models.work_history import WorkHistory
    from db.models.scheduled_notification import ScheduledNotification
    from db.models.transaction import Transaction


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    business_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    client_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    master_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("masters.id", ondelete="CASCADE"), nullable=False, index=True
    )

    service_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("services.id", ondelete="SET NULL"), nullable=True, index=True
    )

    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="booked")
    source: Mapped[str | None] = mapped_column(String(32), nullable=True)

    price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)

    comment: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    created_by_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    business: Mapped["Business"] = relationship(back_populates="appointments")
    client: Mapped["Client"] = relationship(back_populates="appointments")
    master: Mapped["Master"] = relationship(back_populates="appointments")
    service: Mapped["Service | None"] = relationship(back_populates="appointments")
    created_by_user: Mapped["User | None"] = relationship(back_populates="created_appointments")

    work_history: Mapped[list["WorkHistory"]] = relationship(back_populates="appointment")
    scheduled_notifications: Mapped[list["ScheduledNotification"]] = relationship(back_populates="appointment")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="appointment")
