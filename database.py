import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

URL = os.getenv("DATABASE_URL")

if URL is None:
    raise RuntimeError("Cannot get dtabase url")

engine = create_async_engine(URL)

AsyncSession = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSession() as session:
        yield session
