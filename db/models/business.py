from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base

if TYPE_CHECKING:
    from db.models.user import User
    from db.models.master import Master
    from db.models.client import Client
    from db.models.service_category import ServiceCategory
    from db.models.service import Service
    from db.models.master_service import MasterService
    from db.models.master_working_hour import MasterWorkingHour
    from db.models.master_time_off import MasterTimeOff
    from db.models.appointment import Appointment
    from db.models.work_history import WorkHistory
    from db.models.notification_template import NotificationTemplate
    from db.models.scheduled_notification import ScheduledNotification
    from db.models.finance_category import FinanceCategory
    from db.models.transaction import Transaction
    from db.models.portfolio_album import PortfolioAlbum
    from db.models.portfolio_image import PortfolioImage
    from db.models.business_setting import BusinessSetting
    from db.models.bot_config import BotConfig


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    timezone: Mapped[str] = mapped_column(String(64), nullable=False, server_default=text("'Europe/Moscow'"))
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default=text("'EUR'"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    users: Mapped[list["User"]] = relationship(back_populates="business", cascade="all, delete-orphan", passive_deletes=True)
    masters: Mapped[list["Master"]] = relationship(back_populates="business", cascade="all, delete-orphan", passive_deletes=True)
    clients: Mapped[list["Client"]] = relationship(back_populates="business", cascade="all, delete-orphan", passive_deletes=True)

    service_categories: Mapped[list["ServiceCategory"]] = relationship(back_populates="business", cascade="all, delete-orphan", passive_deletes=True)
    services: Mapped[list["Service"]] = relationship(back_populates="business", cascade="all, delete-orphan", passive_deletes=True)
    master_services: Mapped[list["MasterService"]] = relationship(back_populates="business", cascade="all, delete-orphan", passive_deletes=True)

    master_working_hours: Mapped[list["MasterWorkingHour"]] = relationship(back_populates="business", cascade="all, delete-orphan", passive_deletes=True)
    master_time_off: Mapped[list["MasterTimeOff"]] = relationship(back_populates="business", cascade="all, delete-orphan", passive_deletes=True)
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="business", cascade="all, delete-orphan", passive_deletes=True)

    work_history: Mapped[list["WorkHistory"]] = relationship(back_populates="business", cascade="all, delete-orphan", passive_deletes=True)

    notification_templates: Mapped[list["NotificationTemplate"]] = relationship(back_populates="business", cascade="all, delete-orphan", passive_deletes=True)
    scheduled_notifications: Mapped[list["ScheduledNotification"]] = relationship(back_populates="business", cascade="all, delete-orphan", passive_deletes=True)

    finance_categories: Mapped[list["FinanceCategory"]] = relationship(back_populates="business", cascade="all, delete-orphan", passive_deletes=True)
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="business", cascade="all, delete-orphan", passive_deletes=True)

    portfolio_albums: Mapped[list["PortfolioAlbum"]] = relationship(back_populates="business", cascade="all, delete-orphan", passive_deletes=True)
    portfolio_images: Mapped[list["PortfolioImage"]] = relationship(back_populates="business", cascade="all, delete-orphan", passive_deletes=True)

    settings: Mapped["BusinessSetting | None"] = relationship(
        back_populates="business", uselist=False, cascade="all, delete-orphan", passive_deletes=True
    )

    bot_config: Mapped["BotConfig | None"] = relationship(
        back_populates="business", uselist=False, cascade="all, delete-orphan", passive_deletes=True
    )
