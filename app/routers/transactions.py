from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user, get_tenant_business_id, require_permission
from app.schemas import TransactionCreate, TransactionOut
from db.models.transaction import Transaction
from db.models.user import User

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("/", response_model=list[TransactionOut], dependencies=[Depends(require_permission("finance:read"))])
async def list_transactions(
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
) -> list[TransactionOut]:
    result = await session.execute(
        select(Transaction)
        .where(Transaction.business_id == business_id)
        .order_by(Transaction.occurred_at.desc(), Transaction.created_at.desc())
        .limit(500)
    )
    items = result.scalars().all()

    return [
        TransactionOut(
            id=int(t.id),
            occurred_at=t.occurred_at,
            type=t.type,
            amount=int(t.amount),
            comment=t.description,
        )
        for t in items
    ]


@router.post("/", response_model=TransactionOut, dependencies=[Depends(require_permission("finance:write"))])
async def create_transaction(
    payload: TransactionCreate,
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TransactionOut:
    occurred_at = payload.occurred_at
    if occurred_at is None:
        occurred_at = datetime.now(tz=timezone.utc)

    if payload.type not in {"income", "expense"}:
        raise HTTPException(status_code=422, detail="Invalid transaction type")

    tr = Transaction(
        business_id=business_id,
        type=payload.type,
        amount=payload.amount,
        occurred_at=occurred_at,
        description=payload.comment,
        created_by_user_id=int(current_user.id),
    )

    session.add(tr)
    await session.commit()

    return TransactionOut(
        id=int(tr.id),
        occurred_at=tr.occurred_at,
        type=tr.type,
        amount=int(tr.amount),
        comment=tr.description,
    )
