from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

Database_URL = "sqlite+aiosqlite:///./bot.db"

engine = create_async_engine(Database_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
