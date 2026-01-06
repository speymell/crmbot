from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base

if TYPE_CHECKING:
    from db.models.business import Business
    from db.models.user import User
    from db.models.master_service import MasterService
    from db.models.master_working_hour import MasterWorkingHour
    from db.models.master_time_off import MasterTimeOff
    from db.models.appointment import Appointment
    from db.models.work_history import WorkHistory
    from db.models.portfolio_image import PortfolioImage


class Master(Base):
    __tablename__ = "masters"
    __table_args__ = (
        UniqueConstraint("business_id", "user_id", name="uq_masters_business_user"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    business_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    is_bookable: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    business: Mapped["Business"] = relationship(back_populates="masters")
    user: Mapped["User | None"] = relationship(back_populates="master_profile")

    master_services: Mapped[list["MasterService"]] = relationship(back_populates="master", cascade="all, delete-orphan", passive_deletes=True)
    working_hours: Mapped[list["MasterWorkingHour"]] = relationship(back_populates="master", cascade="all, delete-orphan", passive_deletes=True)
    time_off: Mapped[list["MasterTimeOff"]] = relationship(back_populates="master", cascade="all, delete-orphan", passive_deletes=True)

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="master", cascade="all, delete-orphan", passive_deletes=True)
    work_history: Mapped[list["WorkHistory"]] = relationship(back_populates="master", cascade="all, delete-orphan", passive_deletes=True)

    portfolio_images: Mapped[list["PortfolioImage"]] = relationship(back_populates="master")
