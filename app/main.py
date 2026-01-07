from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aiogram import Dispatcher

from app.bot_manager import BotManager
from app.config import settings
from app.db import init_models
from app.logging_setup import setup_logging
from app.routers import analytics, appointments, auth, bots, chat, clients, masters, messages, modules, services, transactions, users, webhook
from handlers import all_routers


def create_app() -> FastAPI:
    setup_logging(settings.log_level)

    fastapi_app = FastAPI(title="BotCRM")

    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    dp = Dispatcher()
    for r in all_routers:
        dp.include_router(r)

    bot_manager = BotManager(dispatcher=dp)

    def get_bot_manager() -> BotManager:
        return bot_manager

    fastapi_app.dependency_overrides[webhook.get_bot_manager] = get_bot_manager
    fastapi_app.dependency_overrides[messages.get_bot_manager] = get_bot_manager

    fastapi_app.include_router(auth.router)
    fastapi_app.include_router(analytics.router)
    fastapi_app.include_router(services.router)
    fastapi_app.include_router(appointments.router)
    fastapi_app.include_router(masters.router)
    fastapi_app.include_router(clients.router)
    fastapi_app.include_router(transactions.router)
    fastapi_app.include_router(chat.router)
    fastapi_app.include_router(modules.router)
    fastapi_app.include_router(users.router)
    fastapi_app.include_router(bots.router)
    fastapi_app.include_router(messages.router)
    fastapi_app.include_router(webhook.router)

    @fastapi_app.on_event("startup")
    async def on_startup() -> None:
        await init_models()

    @fastapi_app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    return fastapi_app


app = create_app()
