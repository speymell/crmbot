from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat_storage import log_message
from app.bot_manager import BotManager
from app.db import get_session

router = APIRouter(tags=["webhook"])


def get_bot_manager() -> BotManager:
    raise RuntimeError("BotManager is not configured")


@router.post("/webhook/{bot_token}")
async def webhook(
    bot_token: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    bot_manager: BotManager = Depends(get_bot_manager),
) -> dict:
    update = await request.json()

    business_id = await bot_manager.get_business_id_by_token(session, bot_token)
    if not business_id:
        raise HTTPException(status_code=404, detail="Unknown bot")

    msg = update.get("message")
    if isinstance(msg, dict):
        text = msg.get("text")
        from_user = msg.get("from")
        if isinstance(text, str) and isinstance(from_user, dict):
            tg_user_id = from_user.get("id")
            if isinstance(tg_user_id, int):
                username = from_user.get("username")
                first_name = from_user.get("first_name")
                last_name = from_user.get("last_name")

                title = None
                if isinstance(username, str) and username:
                    title = f"@{username}" if not username.startswith("@") else username
                else:
                    fn = first_name if isinstance(first_name, str) else ""
                    ln = last_name if isinstance(last_name, str) else ""
                    title = (f"{fn} {ln}").strip() or f"tg:{tg_user_id}"

                await log_message(
                    session,
                    business_id=int(business_id),
                    client_tg_user_id=tg_user_id,
                    title=title,
                    direction="in",
                    text=text,
                    tg_message_id=msg.get("message_id") if isinstance(msg.get("message_id"), int) else None,
                )
                await session.commit()

    await bot_manager.feed_update(bot_token=bot_token, business_id=int(business_id), update_data=update)
    return {"ok": True}
