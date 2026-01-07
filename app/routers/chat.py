from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_tenant_business_id, require_permission
from app.schemas import ChatMessageOut, ChatThreadOut
from db.models.chat_message import ChatMessage
from db.models.chat_thread import ChatThread

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/threads", response_model=list[ChatThreadOut], dependencies=[Depends(require_permission("chat:read"))])
async def list_threads(
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
) -> list[ChatThreadOut]:
    result = await session.execute(
        select(ChatThread)
        .where(ChatThread.business_id == business_id)
        .order_by(ChatThread.updated_at.desc())
        .limit(200)
    )
    items = result.scalars().all()

    return [
        ChatThreadOut(
            id=str(int(t.id)),
            client_tg_user_id=int(t.client_tg_user_id),
            title=t.title,
            updated_at=t.updated_at,
        )
        for t in items
    ]


@router.get("/threads/{thread_id}/messages", response_model=list[ChatMessageOut], dependencies=[Depends(require_permission("chat:read"))])
async def list_messages(
    thread_id: int,
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
) -> list[ChatMessageOut]:
    result = await session.execute(
        select(ChatThread.id).where(ChatThread.id == thread_id, ChatThread.business_id == business_id)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Thread not found")

    result = await session.execute(
        select(ChatMessage)
        .where(ChatMessage.business_id == business_id, ChatMessage.thread_id == thread_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(1000)
    )
    items = result.scalars().all()

    return [
        ChatMessageOut(
            id=str(int(m.id)),
            thread_id=str(int(m.thread_id)),
            direction=m.direction,
            text=m.text,
            created_at=m.created_at,
        )
        for m in items
    ]
