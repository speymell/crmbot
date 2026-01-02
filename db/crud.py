from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.user import User

async def get_or_create_user(session: AsyncSession, telegram_id: int, name: str):
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if user:
        return user

    user = User(
        telegram_id=telegram_id,
        name=name,
    )

    session.add(user)
    await session.commit()
    return user
