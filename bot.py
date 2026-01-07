import os
import asyncio
import logging

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db.session import engine, AsyncSessionLocal
from db.base import Base
from db.crud import get_or_create_client, get_masters_from_db

import db.models  # чтобы модели зарегистрировались

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in .env")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def masters_menu_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Мастера", callback_data="view_masters")]
        ]
    )

def masters_list_kb(masters: list[tuple[int, str]]):
    keyboard = []

    for master_id, master_name in masters:
        keyboard.append([
            InlineKeyboardButton(
                text=master_name,
                callback_data=f"master_{master_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_menu")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.callback_query(F.data == "view_masters")
async def view_masters(callback: types.CallbackQuery):
    masters = await get_masters_from_db()

    if not masters:
        await callback.message.edit_text("Мастеров пока нет 😢")
    else:
        await callback.message.edit_text(
            "Выберите мастера:",
            reply_markup=masters_list_kb(masters)
        )

    await callback.answer()

@dp.callback_query(F.data.startswith("master_"))
async def view_master(callback: types.CallbackQuery):
    master_id = int(callback.data.split("_")[1])

    # позже здесь будет запрос портфолио по master_id
    await callback.message.edit_text(
        f"Портфолио мастера #{master_id}\n(заглушка)"
    )

    await callback.answer()

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выберите действие:",
        reply_markup=masters_menu_kb()
    )
    await callback.answer()

logging.basicConfig(level=logging.INFO)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    async with AsyncSessionLocal() as session:
        await get_or_create_client(
            session=session,
            telegram_id=message.from_user.id,
            name=message.from_user.username,
        )

masssiv = [1, 2, 3, 4, 5, "bebra"]

#@dp.message(Command("testovayacomanda"))
#async def cmd_testovayacomanda(message: types.Message):
#    for item in masssiv:
#        await message.answer("Вот твой массив: " + str(item))

async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
