from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create base class for declarative models
Base = declarative_base()

# Create an asynchronous engine
engine = create_async_engine(
    "sqlite+aiosqlite:///db.sqlite3",
    connect_args={"check_same_thread": False},
    echo=False,
)

# Create an asynchronous session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)


@asynccontextmanager
async def GetDB() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an asynchronous database session to the application.
    """
    async with AsyncSessionLocal() as session:
        yield session
