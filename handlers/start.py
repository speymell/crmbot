from aiogram import Router, types
from aiogram.filters import Command

from db.session import AsyncSessionLocal
from db.crud import get_or_create_client
from keyboards.main_menu import main_menu_kb
from app.tenant import get_business_id

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    async with AsyncSessionLocal() as session:
        business_id = get_business_id() or 1
        await get_or_create_client(
            session=session,
            telegram_id=message.from_user.id,
            name=message.from_user.username,
            business_id=business_id,
        )

    await message.answer("Выберите действие:", reply_markup=main_menu_kb())
