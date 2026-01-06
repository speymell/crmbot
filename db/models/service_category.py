from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from db.models.business import Business
    from db.models.service import Service


class ServiceCategory(Base):
    __tablename__ = "service_categories"
    __table_args__ = (
        UniqueConstraint("business_id", "name", name="uq_service_categories_business_name"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    business_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    business: Mapped["Business"] = relationship(back_populates="service_categories")
    services: Mapped[list["Service"]] = relationship(back_populates="category", cascade="all, delete-orphan", passive_deletes=True)
