from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat_storage import log_message
from app.bot_manager import BotManager
from app.db import get_session
from app.deps import get_tenant_business_id, require_permission
from app.schemas import SendMessageRequest
from db.models.bot_config import BotConfig
from db.models.client import Client

router = APIRouter(prefix="/api/messages", tags=["messages"])


def get_bot_manager() -> BotManager:
    raise RuntimeError("BotManager is not configured")


@router.post("/send")
async def send_message(
    payload: SendMessageRequest,
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
    bot_manager: BotManager = Depends(get_bot_manager),
    _: None = Depends(require_permission("chat:write")),
) -> dict:
    result = await session.execute(
        select(BotConfig).where(BotConfig.business_id == business_id, BotConfig.is_active.is_(True))
    )
    cfg = result.scalar_one_or_none()
    if not cfg or not cfg.bot_token:
        raise HTTPException(status_code=409, detail="Bot token not configured")

    bot = bot_manager.get_bot(cfg.bot_token)
    sent = await bot.send_message(chat_id=payload.client_tg_user_id, text=payload.text)

    result = await session.execute(
        select(Client).where(Client.business_id == business_id, Client.tg_user_id == payload.client_tg_user_id)
    )
    client = result.scalar_one_or_none()
    title = (client.username if client else None) or f"tg:{payload.client_tg_user_id}"

    await log_message(
        session,
        business_id=business_id,
        client_tg_user_id=payload.client_tg_user_id,
        title=title,
        direction="out",
        text=payload.text,
        tg_message_id=int(getattr(sent, "message_id", 0)) or None,
    )
    await session.commit()

    return {"status": "ok"}
