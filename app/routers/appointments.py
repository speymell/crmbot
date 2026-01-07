from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_tenant_business_id, require_permission
from app.schemas import AppointmentCreate, AppointmentOut
from db.models.appointment import Appointment
from db.models.service import Service
from db.models.work_history import WorkHistory

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


@router.get("/", response_model=list[AppointmentOut])
async def list_appointments(
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("appointments:read")),
) -> list[AppointmentOut]:
    result = await session.execute(
        select(Appointment).where(Appointment.business_id == business_id).order_by(Appointment.start_at.desc())
    )
    items = result.scalars().all()

    return [
        AppointmentOut(
            id=int(a.id),
            client_id=int(a.client_id),
            master_id=int(a.master_id),
            service_id=int(a.service_id) if a.service_id else None,
            start_at=a.start_at,
            end_at=a.end_at,
            status=a.status,
            price=a.price,
            duration_min=a.duration_min,
        )
        for a in items
    ]


@router.post("/", response_model=AppointmentOut)
async def create_appointment(
    payload: AppointmentCreate,
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("appointments:write")),
) -> AppointmentOut:
    appt = Appointment(
        business_id=business_id,
        client_id=payload.client_id,
        master_id=payload.master_id,
        service_id=payload.service_id,
        start_at=payload.start_at,
        end_at=payload.end_at,
        status="booked",
        source="admin",
        comment=payload.comment,
    )

    session.add(appt)

    price: int | None = None
    duration_min: int | None = None
    service_name = "Запись"

    if payload.service_id is not None:
        result = await session.execute(
            select(Service).where(
                Service.id == payload.service_id,
                Service.business_id == business_id,
            )
        )
        s = result.scalar_one_or_none()
        if s is not None:
            price = int(s.price)
            duration_min = int(s.duration_min)
            service_name = s.name

    appt.price = price
    appt.duration_min = duration_min

    await session.flush()

    wh = WorkHistory(
        business_id=business_id,
        appointment_id=int(appt.id),
        client_id=int(appt.client_id),
        master_id=int(appt.master_id),
        service_name=service_name,
        price=price,
    )
    session.add(wh)

    await session.commit()

    return AppointmentOut(
        id=int(appt.id),
        client_id=int(appt.client_id),
        master_id=int(appt.master_id),
        service_id=int(appt.service_id) if appt.service_id else None,
        start_at=appt.start_at,
        end_at=appt.end_at,
        status=appt.status,
        price=appt.price,
        duration_min=appt.duration_min,
    )
