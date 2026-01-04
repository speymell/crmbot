import os
import asyncio
import logging

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

from db.session import engine, AsyncSessionLocal
from db.base import Base
from db.crud import get_or_create_user

import db.models  # чтобы модели зарегистрировались

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in .env")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    async with AsyncSessionLocal() as session:
        await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            name=message.from_user.username,
        )
    await message.answer(f"Ты был успешно зарегистрирован в базе данных! {message.from_user.username}")
    await message.answer("Привет! Я бот на aiogram.")


masssiv = [1, 2, 3, 4, 5, "bebra"]


@dp.message(Command("testovayacomanda"))
async def cmd_testovayacomanda(message: types.Message):
    for item in masssiv:
        await message.answer("Вот твой массив: " + str(item))


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
