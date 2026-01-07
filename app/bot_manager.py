import hashlib
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties as DefaultBotProperties
from aiogram.types import Update
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.tenant import set_business_id
from db.models.bot_config import BotConfig


def bot_token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class BotManager:
    def __init__(self, dispatcher: Dispatcher):
        self._dp = dispatcher
        self._bots: dict[str, Bot] = {}

    async def get_business_id_by_token(self, session: AsyncSession, bot_token: str) -> int | None:
        token_hash = bot_token_hash(bot_token)
        result = await session.execute(
            select(BotConfig.business_id).where(BotConfig.bot_token_hash == token_hash, BotConfig.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    def get_bot(self, bot_token: str) -> Bot:
        bot = self._bots.get(bot_token)
        if bot:
            return bot

        bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode="HTML"))
        self._bots[bot_token] = bot
        return bot

    async def feed_update(self, *, bot_token: str, business_id: int, update_data: dict[str, Any]) -> None:
        bot = self.get_bot(bot_token)
        update = Update.model_validate(update_data)
        set_business_id(business_id)
        await self._dp.feed_update(bot, update)
