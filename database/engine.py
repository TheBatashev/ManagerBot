from typing import Union, Any

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine import URL

BaseModel = declarative_base()



# def get_db_url():
#     return URL.create(
#         drivername='postgresql+asyncpg',
#         username=,
#         password=,
#         host=,
#         port=,
#         database=
#     )

def create_engine() -> AsyncEngine:
    return create_async_engine(url='sqlite+aiosqlite:///db.sqlite3', echo=False, pool_pre_ping=True)


def get_session_maker(engine: AsyncEngine) -> async_sessionmaker[Union[AsyncSession, Any]]:
    return async_sessionmaker(bind=engine, class_=AsyncSession, autoflush=True)


async def init_models():
    engine = create_engine()
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


