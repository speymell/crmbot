from aiogram import Router, F, types

from sqlalchemy import select

from app.tenant import get_business_id
from db.models.service import Service
from db.session import AsyncSessionLocal

router = Router()


@router.message(F.text == "Цены на услуги")
async def get_prices(message: types.Message):
    business_id = get_business_id() or 1

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Service)
            .where(Service.business_id == business_id, Service.is_active.is_(True))
            .order_by(Service.sort_order, Service.name)
        )
        services = result.scalars().all()

    if not services:
        await message.answer("Пока нет услуг")
        return

    lines: list[str] = []
    for s in services:
        lines.append(f"{s.name} = {s.price}")

    await message.answer("\n".join(lines))
