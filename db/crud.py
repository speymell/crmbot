from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.client import Client


async def get_or_create_client(session: AsyncSession, telegram_id: int, name: str, business_id: int = 1):
    result = await session.execute(
        select(Client).where(Client.business_id == business_id, Client.tg_user_id == telegram_id)
    )
    client = result.scalar_one_or_none()

    if client:
        return client

    client = Client(
        tg_user_id=telegram_id,
        username=name,
        business_id=business_id  # временно жестко задаем бизнес_id = 1
    )

    session.add(client)
    await session.commit()
    return client


async def get_masters_from_db():
    # тут типо настоящие данные
    return [
        (1, "Анна"),
        (2, "Иван"),
        (3, "Мария")
    ]