from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_tenant_business_id, require_permission
from app.schemas import ModulesResponse, ModulesUpdate
from db.models.business_modules import BusinessModules

router = APIRouter(prefix="/api/modules", tags=["modules"])


@router.get("", response_model=ModulesResponse)
async def get_modules(
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
) -> ModulesResponse:
    result = await session.execute(select(BusinessModules).where(BusinessModules.business_id == business_id))
    row = result.scalar_one_or_none()
    modules = (row.modules if row and isinstance(row.modules, dict) else {})
    return ModulesResponse(modules=modules)


@router.put("", response_model=ModulesResponse, dependencies=[Depends(require_permission("bots:write"))])
async def set_modules(
    payload: ModulesUpdate,
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
) -> ModulesResponse:
    result = await session.execute(select(BusinessModules).where(BusinessModules.business_id == business_id))
    row = result.scalar_one_or_none()

    if row is None:
        row = BusinessModules(business_id=business_id, modules=payload.modules)
        session.add(row)
    else:
        row.modules = payload.modules

    await session.commit()
    return ModulesResponse(modules=row.modules)
