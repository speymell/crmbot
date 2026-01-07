from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot_manager import bot_token_hash
from app.db import get_session
from app.deps import get_tenant_business_id, require_permission
from app.schemas import BotTokenSetRequest
from db.models.bot_config import BotConfig

router = APIRouter(prefix="/api/bots", tags=["bots"])


@router.post("/set-token")
async def set_bot_token(
    payload: BotTokenSetRequest,
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("bots:write")),
) -> dict:
    result = await session.execute(select(BotConfig).where(BotConfig.business_id == business_id))
    cfg = result.scalar_one_or_none()

    token_hash = bot_token_hash(payload.bot_token)

    if cfg is None:
        cfg = BotConfig(business_id=business_id, bot_token=payload.bot_token, bot_token_hash=token_hash, is_active=True)
        session.add(cfg)
    else:
        cfg.bot_token = payload.bot_token
        cfg.bot_token_hash = token_hash
        cfg.is_active = True

    await session.commit()

    return {"status": "ok"}
