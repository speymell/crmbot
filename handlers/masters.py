from aiogram import Router, F, types

from db.crud import get_masters_from_db
from keyboards.master_menu import masters_list_kb

router = Router()


@router.message(F.text == "Мастера")
async def view_masters(message: types.Message):
    masters = await get_masters_from_db()

    if not masters:
        await message.answer("Мастеров пока нет 😢")
        return

    await message.answer(
        "Выберите мастера:",
        reply_markup=masters_list_kb(masters),
    )


@router.callback_query(F.data.startswith("master_"))
async def view_master(callback: types.CallbackQuery):
    master_id = int(callback.data.split("_")[1])

    await callback.message.edit_text(
        f"Портфолио мастера #{master_id}\n(заглушка)"
    )
    await callback.answer()
