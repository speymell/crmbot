# db/models/businesses.py
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, BigInteger, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base

if TYPE_CHECKING:
    from db.models.users import User
    from db.models.masters import Master
    from db.models.clients import Client
    from db.models.service_categories import ServiceCategories
    from db.models.services import Services
    from db.models.master_services import MasterServices
    from db.models.master_working_hours import MasterWorkingHours


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    timezone: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        server_default=text("'Europe/Moscow'"),
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        server_default=text("'EUR'"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    users: Mapped[list["User"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    masters: Mapped[list["Master"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    clients: Mapped[list["Client"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    service_categories: Mapped[list["ServiceCategories"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    services: Mapped[list["Services"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    master_services: Mapped[list["MasterServices"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    master_working_hours: Mapped[list["MasterWorkingHours"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
