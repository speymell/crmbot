from datetime import datetime

from pydantic import BaseModel


class RegisterRequest(BaseModel):
    business_name: str
    email: str
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    business_id: int
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ServiceCreate(BaseModel):
    category_id: int
    name: str
    description: str | None = None
    duration_min: int
    price: int


class ServiceOut(BaseModel):
    id: int
    category_id: int
    name: str
    description: str | None
    duration_min: int
    price: int
    is_active: bool


class AppointmentCreate(BaseModel):
    client_id: int
    master_id: int
    service_id: int | None = None
    start_at: datetime
    end_at: datetime
    comment: str | None = None


class AppointmentOut(BaseModel):
    id: int
    client_id: int
    master_id: int
    service_id: int | None
    start_at: datetime
    end_at: datetime
    status: str
    price: int | None
    duration_min: int | None


class AnalyticsResponse(BaseModel):
    occupancy: list[dict]
    finance: list[dict]


class BotTokenSetRequest(BaseModel):
    bot_token: str


class SendMessageRequest(BaseModel):
    client_tg_user_id: int
    text: str


class MasterCreate(BaseModel):
    display_name: str
    bio: str | None = None
    is_bookable: bool | None = None


class MasterOut(BaseModel):
    id: int
    display_name: str
    bio: str | None
    is_bookable: bool


class ClientOut(BaseModel):
    id: int
    tg_user_id: int | None
    username: str | None
    phone: str | None


class TransactionCreate(BaseModel):
    occurred_at: datetime | None = None
    type: str
    amount: int
    comment: str | None = None


class TransactionOut(BaseModel):
    id: int
    occurred_at: datetime | None
    type: str
    amount: int
    comment: str | None


class ChatThreadOut(BaseModel):
    id: str
    client_tg_user_id: int
    title: str
    updated_at: datetime


class ChatMessageOut(BaseModel):
    id: str
    thread_id: str
    direction: str
    text: str
    created_at: datetime


class WorkHistoryOut(BaseModel):
    id: int
    client_id: int
    master_id: int
    service_name: str
    price: int | None
    created_at: datetime


class ModulesResponse(BaseModel):
    modules: dict


class ModulesUpdate(BaseModel):
    modules: dict


class UserOut(BaseModel):
    id: int
    email: str | None
    full_name: str | None
    role: str
    is_active: bool


class UserCreate(BaseModel):
    email: str
    password: str | None = None
    full_name: str | None = None
    role: str = "staff"


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: str | None = None
    is_active: bool | None = None
    password: str | None = None


class UserPermissionsOut(BaseModel):
    user_id: int
    permissions: dict


class UserPermissionsUpdate(BaseModel):
    permissions: dict
