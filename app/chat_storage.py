from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.chat_message import ChatMessage
from db.models.chat_thread import ChatThread
from db.models.client import Client


async def ensure_client(session: AsyncSession, *, business_id: int, tg_user_id: int, username: str | None) -> None:
    result = await session.execute(
        select(Client.id).where(Client.business_id == business_id, Client.tg_user_id == tg_user_id)
    )
    if result.scalar_one_or_none() is not None:
        return

    client = Client(business_id=business_id, tg_user_id=tg_user_id, username=username)
    session.add(client)


async def get_or_create_thread(
    session: AsyncSession, *, business_id: int, client_tg_user_id: int, title: str
) -> ChatThread:
    result = await session.execute(
        select(ChatThread).where(
            ChatThread.business_id == business_id,
            ChatThread.client_tg_user_id == client_tg_user_id,
        )
    )
    thread = result.scalar_one_or_none()

    now = datetime.now(tz=timezone.utc)

    if thread is None:
        thread = ChatThread(
            business_id=business_id,
            client_tg_user_id=client_tg_user_id,
            title=title,
            updated_at=now,
        )
        session.add(thread)
        await session.flush()
        return thread

    # keep title up to date if better title is known
    if title and thread.title != title:
        thread.title = title

    thread.updated_at = now
    return thread


async def log_message(
    session: AsyncSession,
    *,
    business_id: int,
    client_tg_user_id: int,
    title: str,
    direction: str,
    text: str,
    tg_message_id: int | None = None,
) -> ChatMessage:
    await ensure_client(session, business_id=business_id, tg_user_id=client_tg_user_id, username=title)
    thread = await get_or_create_thread(
        session,
        business_id=business_id,
        client_tg_user_id=client_tg_user_id,
        title=title,
    )

    msg = ChatMessage(
        business_id=business_id,
        thread_id=int(thread.id),
        direction=direction,
        text=text,
        tg_message_id=tg_message_id,
    )
    session.add(msg)
    return msg
