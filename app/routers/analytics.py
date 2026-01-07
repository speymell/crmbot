from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_tenant_business_id
from app.schemas import AnalyticsResponse
from db.models.appointment import Appointment
from db.models.transaction import Transaction

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/", response_model=AnalyticsResponse)
async def analytics(
    start: datetime | None = None,
    end: datetime | None = None,
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
) -> AnalyticsResponse:
    appt_q = select(
        func.date_trunc("hour", Appointment.start_at).label("ts"),
        func.count(Appointment.id).label("count"),
    ).where(Appointment.business_id == business_id)

    if start is not None:
        appt_q = appt_q.where(Appointment.start_at >= start)
    if end is not None:
        appt_q = appt_q.where(Appointment.start_at < end)

    appt_q = appt_q.group_by("ts").order_by("ts")

    result = await session.execute(appt_q)
    occupancy = [{"ts": row.ts.isoformat(), "count": int(row.count)} for row in result.all()]

    tr_q = select(
        func.date_trunc("day", Transaction.occurred_at).label("day"),
        Transaction.type.label("type"),
        func.sum(Transaction.amount).label("amount"),
    ).where(Transaction.business_id == business_id, Transaction.occurred_at.is_not(None))

    if start is not None:
        tr_q = tr_q.where(Transaction.occurred_at >= start)
    if end is not None:
        tr_q = tr_q.where(Transaction.occurred_at < end)

    tr_q = tr_q.group_by("day", "type").order_by("day")

    result = await session.execute(tr_q)
    finance = [
        {"day": row.day.date().isoformat() if row.day else None, "type": row.type, "amount": int(row.amount or 0)}
        for row in result.all()
    ]

    return AnalyticsResponse(occupancy=occupancy, finance=finance)
