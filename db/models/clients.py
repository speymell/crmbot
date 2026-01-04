from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, String, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.testing.schema import mapped_column

from db.base import Base
from sqlalchemy.sql import func

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.models.businesses import Business


class Client(Base):
    __tablename__ = "clients"

    __table_args__ = (
        UniqueConstraint("business_id", "tg_user_id", name="uq_clients_business_tg"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    business_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("businesses.id", ondelete="cascade"),
        nullable = False,
        index = True,
    )

    tg_user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable = True,
        index = True,
    )

    phone: Mapped[str | None] = mapped_column(String(32), nullable = True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)

    last_visit_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable = True,
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default = func.now(),
        nullable = True,
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True,
        onupdate=func.now(),
    )

    business: Mapped["Business"] = relationship(back_populates="clients")