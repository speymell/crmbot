from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_tenant_business_id, require_permission
from app.schemas import ClientOut, WorkHistoryOut
from db.models.client import Client
from db.models.work_history import WorkHistory

router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.get("/", response_model=list[ClientOut], dependencies=[Depends(require_permission("clients:read"))])
async def list_clients(
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
) -> list[ClientOut]:
    result = await session.execute(
        select(Client).where(Client.business_id == business_id).order_by(Client.updated_at.desc())
    )
    items = result.scalars().all()

    return [
        ClientOut(
            id=int(c.id),
            tg_user_id=int(c.tg_user_id) if c.tg_user_id is not None else None,
            username=c.username,
            phone=c.phone,
        )
        for c in items
    ]


@router.get("/{client_id}/history", response_model=list[WorkHistoryOut], dependencies=[Depends(require_permission("clients:read"))])
async def client_history(
    client_id: int,
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
) -> list[WorkHistoryOut]:
    result = await session.execute(
        select(Client.id).where(Client.id == client_id, Client.business_id == business_id)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Client not found")

    result = await session.execute(
        select(WorkHistory)
        .where(WorkHistory.business_id == business_id, WorkHistory.client_id == client_id)
        .order_by(WorkHistory.created_at.desc())
        .limit(200)
    )
    items = result.scalars().all()

    return [
        WorkHistoryOut(
            id=int(w.id),
            client_id=int(w.client_id),
            master_id=int(w.master_id),
            service_name=w.service_name,
            price=int(w.price) if w.price is not None else None,
            created_at=w.created_at,
        )
        for w in items
    ]
