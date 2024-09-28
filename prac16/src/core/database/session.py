import functools
from typing import AsyncGenerator, Callable, Awaitable
from contextlib import asynccontextmanager

from core.settings import config

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select


engine = create_async_engine(
    url=config.DATABASE_URL.unicode_string(),
    pool_size=10,
    max_overflow = 0,
    pool_pre_ping = True,
    connect_args = {
        "timeout": 30,
        "command_timeout": 15,
        "server_settings": {
            "jit": "off",
            "application_name": config.DATABASE_CONNECTION_APP_NAME,
        },
    },
    echo=config.ECHO_SQL
)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_pg_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as db_session:
        yield db_session


@asynccontextmanager
async def context_get_pg_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as db_session:
        yield db_session


def provide_pg_session(
    func: Callable[..., Awaitable]
) -> Callable[..., Awaitable]:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        async with context_get_pg_session() as db_session:
            return await func(*args, session=db_session, **kwargs)
    return wrapper

@provide_pg_session
async def test_pg_connection(session: AsyncSession):
    result = await session.execute(select(1))
    return f"PostgreSQL `SELECT(1)` returned: {result.scalar()}"

