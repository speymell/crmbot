from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base

if TYPE_CHECKING:
    from db.models.business import Business
    from db.models.portfolio_album import PortfolioAlbum
    from db.models.master import Master
    from db.models.service import Service


class PortfolioImage(Base):
    __tablename__ = "portfolio_images"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    business_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    album_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("portfolio_albums.id", ondelete="SET NULL"), nullable=True, index=True
    )
    master_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("masters.id", ondelete="SET NULL"), nullable=True, index=True
    )
    service_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("services.id", ondelete="SET NULL"), nullable=True, index=True
    )

    file_url: Mapped[str] = mapped_column(String(2000), nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    business: Mapped["Business"] = relationship(back_populates="portfolio_images")
    album: Mapped["PortfolioAlbum | None"] = relationship(back_populates="images")
    master: Mapped["Master | None"] = relationship(back_populates="portfolio_images")
    service: Mapped["Service | None"] = relationship(back_populates="portfolio_images")
