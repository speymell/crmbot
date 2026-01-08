from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.security import create_access_token, hash_password, verify_password
from db.models.business import Business
from db.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    business = Business(name=payload.business_name)
    session.add(business)
    await session.flush()

    result = await session.execute(
        select(User).where(User.business_id == business.id, User.email == payload.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="User already exists")

    user = User(
        business_id=business.id,
        role="owner",
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        is_active=True,
    )
    session.add(user)
    await session.commit()

    token = create_access_token(user_id=int(user.id), business_id=int(business.id), role=user.role)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    result = await session.execute(
        select(User).where(User.business_id == payload.business_id, User.email == payload.email, User.is_active.is_(True))
    )
    user = result.scalar_one_or_none()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user_id=int(user.id), business_id=int(user.business_id), role=user.role)
    return TokenResponse(access_token=token)
