from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Boolean, Integer, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from db.models.businesses import Business
    from db.models.masters import Master
    from db.models.services import Services


class MasterServices(Base):
    __tablename__ = "master_services"
    __table_args__ = (
        UniqueConstraint("business_id", "master_id", "service_id", name="uq_master_service"),
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

    service_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # кастомные значения: если NULL — берём из Services
    custom_price_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    custom_duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    business: Mapped["Business"] = relationship(back_populates="master_services")
    master: Mapped["Master"] = relationship(back_populates="master_services")
    service: Mapped["Services"] = relationship(back_populates="master_services")
