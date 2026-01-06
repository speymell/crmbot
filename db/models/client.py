from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base

if TYPE_CHECKING:
    from db.models.business import Business
    from db.models.appointment import Appointment
    from db.models.work_history import WorkHistory
    from db.models.scheduled_notification import ScheduledNotification


class Client(Base):
    __tablename__ = "clients"
    __table_args__ = (
        UniqueConstraint("business_id", "tg_user_id", name="uq_clients_business_tg"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    business_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    tg_user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)

    last_visit_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    business: Mapped["Business"] = relationship(back_populates="clients")

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="client", cascade="all, delete-orphan", passive_deletes=True)
    work_history: Mapped[list["WorkHistory"]] = relationship(back_populates="client", cascade="all, delete-orphan", passive_deletes=True)
    scheduled_notifications: Mapped[list["ScheduledNotification"]] = relationship(back_populates="client", cascade="all, delete-orphan", passive_deletes=True)
