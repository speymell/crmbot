from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import PyJWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.security import decode_access_token
from app.tenant import set_business_id
from db.models.user import User
from db.models.user_permission import UserPermission

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id_raw = payload.get("sub")
    business_id = payload.get("business_id")

    if not user_id_raw or not business_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = int(user_id_raw)

    result = await session.execute(
        select(User).where(User.id == user_id, User.business_id == business_id, User.is_active.is_(True))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    set_business_id(int(business_id))
    return user


async def get_tenant_business_id(
    current_user: User = Depends(get_current_user),
    x_business_id: int | None = Header(default=None, alias="X-Business-Id"),
) -> int:
    business_id = int(current_user.business_id)

    if x_business_id is not None and int(x_business_id) != business_id:
        raise HTTPException(status_code=403, detail="Business isolation violation")

    set_business_id(business_id)
    return business_id


def _base_allowed_permissions(role: str) -> set[str]:
    all_perms = {
        "services:read",
        "services:write",
        "appointments:read",
        "appointments:write",
        "masters:read",
        "masters:write",
        "clients:read",
        "clients:write",
        "finance:read",
        "finance:write",
        "chat:read",
        "chat:write",
        "bots:write",
        "users:write",
    }

    if role == "owner":
        return set(all_perms)

    if role == "admin":
        return {
            "services:read",
            "services:write",
            "appointments:read",
            "appointments:write",
            "masters:read",
            "masters:write",
            "clients:read",
            "clients:write",
            "finance:read",
            "finance:write",
            "chat:read",
            "chat:write",
            "bots:write",
        }

    # staff
    return {"appointments:read", "clients:read", "chat:read"}


async def _effective_permission_value(*, session: AsyncSession, user: User, permission: str) -> bool:
    allowed = permission in _base_allowed_permissions(user.role)

    result = await session.execute(
        select(UserPermission).where(UserPermission.business_id == user.business_id, UserPermission.user_id == user.id)
    )
    row = result.scalar_one_or_none()
    overrides = row.permissions if row and isinstance(row.permissions, dict) else {}

    if permission in overrides:
        try:
            return bool(overrides[permission])
        except Exception:
            return allowed

    return allowed


def require_permission(permission: str):
    async def _dep(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
    ) -> None:
        ok = await _effective_permission_value(session=session, user=current_user, permission=permission)
        if not ok:
            raise HTTPException(status_code=403, detail="Forbidden")

    return _dep
