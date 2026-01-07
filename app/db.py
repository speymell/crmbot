from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from db.base import Base
from db.session import AsyncSessionLocal, engine
import db.models


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
