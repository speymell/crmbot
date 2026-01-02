from db.session import engine
from db.base import Base
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from db.crud import get_or_create_user
from db.session import AsyncSessionLocal


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

logging.basicConfig(level=logging.INFO)
bot = Bot(token="8075241508:AAESzwdoqv9gZR1SD8xCttwMBvmZUnBhhWs")
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    #await init_db()
    async with AsyncSessionLocal() as session:
        await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            name=message.from_user.username,
        )
        await message.answer("Ты был успешно зарегистрирован в базе данных!" + str(message.from_user.username))
    await message.answer("Привет! Я бот на aiogram.")

masssiv = [1,2,3,4,5,"bebra"]

@dp.message(Command("testovayacomanda"))
async def cmd_testovayacomanda(message: types.Message):
   for i in range(len(masssiv)):
    await message.answer(f"Вот твой массив:" + str(masssiv[i]))

# Запуск процесса поллинга новых апдейтов
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
