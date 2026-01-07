from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user, get_tenant_business_id, require_permission
from app.schemas import UserCreate, UserOut, UserPermissionsOut, UserPermissionsUpdate, UserUpdate
from app.security import hash_password
from db.models.user import User
from db.models.user_permission import UserPermission

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/", response_model=list[UserOut], dependencies=[Depends(require_permission("users:write"))])
async def list_users(
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
) -> list[UserOut]:
    result = await session.execute(
        select(User).where(User.business_id == business_id).order_by(User.created_at.desc()).limit(200)
    )
    items = result.scalars().all()

    return [
        UserOut(
            id=int(u.id),
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            is_active=bool(u.is_active),
        )
        for u in items
    ]


@router.post("/", response_model=UserOut, dependencies=[Depends(require_permission("users:write"))])
async def create_user(
    payload: UserCreate,
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
) -> UserOut:
    if not payload.email:
        raise HTTPException(status_code=422, detail="email is required")

    result = await session.execute(select(User.id).where(User.business_id == business_id, User.email == payload.email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="User already exists")

    user = User(
        business_id=business_id,
        role=payload.role,
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password) if payload.password else None,
        is_active=True,
    )

    session.add(user)
    await session.commit()

    return UserOut(
        id=int(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=bool(user.is_active),
    )


@router.get("/me/permissions", response_model=UserPermissionsOut)
async def get_my_permissions(
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> UserPermissionsOut:
    result = await session.execute(
        select(UserPermission).where(
            UserPermission.business_id == business_id,
            UserPermission.user_id == current_user.id,
        )
    )
    row = result.scalar_one_or_none()
    perms = (row.permissions if row and isinstance(row.permissions, dict) else {})
    return UserPermissionsOut(user_id=int(current_user.id), permissions=perms)


@router.patch("/{user_id}", response_model=UserOut, dependencies=[Depends(require_permission("users:write"))])
async def update_user(
    user_id: int,
    payload: UserUpdate,
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> UserOut:
    if int(current_user.id) == int(user_id) and payload.is_active is False:
        raise HTTPException(status_code=409, detail="Cannot deactivate yourself")

    result = await session.execute(select(User).where(User.id == user_id, User.business_id == business_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.password is not None:
        user.password_hash = hash_password(payload.password)

    await session.commit()

    return UserOut(
        id=int(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=bool(user.is_active),
    )


@router.get("/{user_id}/permissions", response_model=UserPermissionsOut)
async def get_user_permissions(
    user_id: int,
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> UserPermissionsOut:
    if int(current_user.id) != int(user_id) and current_user.role not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Forbidden")

    result = await session.execute(select(User.id).where(User.id == user_id, User.business_id == business_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="User not found")

    result = await session.execute(
        select(UserPermission).where(UserPermission.business_id == business_id, UserPermission.user_id == user_id)
    )
    row = result.scalar_one_or_none()
    perms = (row.permissions if row and isinstance(row.permissions, dict) else {})
    return UserPermissionsOut(user_id=user_id, permissions=perms)


@router.put("/{user_id}/permissions", response_model=UserPermissionsOut)
async def set_user_permissions(
    user_id: int,
    payload: UserPermissionsUpdate,
    business_id: int = Depends(get_tenant_business_id),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> UserPermissionsOut:
    if current_user.role not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Forbidden")

    result = await session.execute(select(User.id).where(User.id == user_id, User.business_id == business_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="User not found")

    result = await session.execute(
        select(UserPermission).where(UserPermission.business_id == business_id, UserPermission.user_id == user_id)
    )
    row = result.scalar_one_or_none()

    if row is None:
        row = UserPermission(business_id=business_id, user_id=user_id, permissions=payload.permissions)
        session.add(row)
    else:
        row.permissions = payload.permissions

    await session.commit()
    return UserPermissionsOut(user_id=user_id, permissions=row.permissions)
