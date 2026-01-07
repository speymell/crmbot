from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_tenant_business_id, require_permission
from app.schemas import ServiceCreate, ServiceOut
from db.models.service import Service

router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("/", response_model=list[ServiceOut])
async def list_services(
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("services:read")),
) -> list[ServiceOut]:
    result = await session.execute(
        select(Service).where(Service.business_id == business_id, Service.is_active.is_(True)).order_by(Service.sort_order)
    )
    services = result.scalars().all()

    return [
        ServiceOut(
            id=int(s.id),
            category_id=int(s.category_id),
            name=s.name,
            description=s.description,
            duration_min=int(s.duration_min),
            price=int(s.price),
            is_active=bool(s.is_active),
        )
        for s in services
    ]


@router.post("/", response_model=ServiceOut)
async def create_service(
    payload: ServiceCreate,
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("services:write")),
) -> ServiceOut:
    service = Service(
        business_id=business_id,
        category_id=payload.category_id,
        name=payload.name,
        description=payload.description,
        duration_min=payload.duration_min,
        price=payload.price,
        is_active=True,
    )

    session.add(service)
    await session.commit()

    return ServiceOut(
        id=int(service.id),
        category_id=int(service.category_id),
        name=service.name,
        description=service.description,
        duration_min=int(service.duration_min),
        price=int(service.price),
        is_active=bool(service.is_active),
    )
