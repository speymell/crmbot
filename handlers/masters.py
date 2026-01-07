from aiogram import Router, F, types

from keyboards.master_menu import masters_list_kb

from sqlalchemy import select

from app.tenant import get_business_id
from db.models.master import Master
from db.session import AsyncSessionLocal

router = Router()


@router.message(F.text == "Мастера")
async def view_masters(message: types.Message):
    business_id = get_business_id() or 1

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Master)
            .where(Master.business_id == business_id, Master.is_bookable.is_(True))
            .order_by(Master.display_name)
        )
        master_rows = result.scalars().all()

    masters = [(int(m.id), m.display_name) for m in master_rows]

    if not masters:
        await message.answer("Мастеров пока нет")
        return

    await message.answer(
        "Выберите мастера:",
        reply_markup=masters_list_kb(masters),
    )


@router.callback_query(F.data.startswith("master_"))
async def view_master(callback: types.CallbackQuery):
    master_id = int(callback.data.split("_")[1])

    business_id = get_business_id() or 1

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Master).where(Master.id == master_id, Master.business_id == business_id)
        )
        master = result.scalar_one_or_none()

    if not master:
        await callback.answer("Мастер не найден", show_alert=True)
        return

    await callback.message.edit_text(
        f"{master.display_name}\n{master.bio or ''}"
    )
    await callback.answer()
