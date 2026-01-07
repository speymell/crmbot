from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_tenant_business_id, require_permission
from app.schemas import MasterCreate, MasterOut
from db.models.master import Master

router = APIRouter(prefix="/api/masters", tags=["masters"])


@router.get("/", response_model=list[MasterOut], dependencies=[Depends(require_permission("masters:read"))])
async def list_masters(
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
) -> list[MasterOut]:
    result = await session.execute(
        select(Master).where(Master.business_id == business_id).order_by(Master.display_name)
    )
    items = result.scalars().all()

    return [
        MasterOut(
            id=int(m.id),
            display_name=m.display_name,
            bio=m.bio,
            is_bookable=bool(m.is_bookable),
        )
        for m in items
    ]


@router.post("/", response_model=MasterOut, dependencies=[Depends(require_permission("masters:write"))])
async def create_master(
    payload: MasterCreate,
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
) -> MasterOut:
    master = Master(
        business_id=business_id,
        display_name=payload.display_name,
        bio=payload.bio,
        is_bookable=payload.is_bookable if payload.is_bookable is not None else True,
    )

    session.add(master)
    await session.commit()

    return MasterOut(
        id=int(master.id),
        display_name=master.display_name,
        bio=master.bio,
        is_bookable=bool(master.is_bookable),
    )
