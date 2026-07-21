from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings
from app.db.url import prepare_asyncpg_url

settings = get_settings()

if settings.database_url.startswith("sqlite"):
    db_url = settings.database_url
    connect_args: dict = {"check_same_thread": False}
else:
    db_url, connect_args = prepare_asyncpg_url(settings.database_url)

engine = create_async_engine(db_url, echo=False, connect_args=connect_args)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
