from contextlib import asynccontextmanager
import datetime
import os
import uuid

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

# Note the change to 'postgresql+asyncpg'
DB_HOST = os.environ['DATABASE_HOST']
DB_PORT = os.environ['DATABASE_PORT']
DB_NAME = os.environ['DATABASE_NAME']
DB_USER = os.environ['DATABASE_USER']
DB_PASS = os.environ['DATABASE_PASSWORD']
ASYNC_SQLALCHEMY_DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Create the async engine
engine = create_async_engine(
    ASYNC_SQLALCHEMY_DATABASE_URL,
    echo=False,  # Set to True to see SQL queries printed to the console
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,     # Automatically close and recreate connections older than 30 mins
    pool_pre_ping=True,    # 👈 Checks if connection is alive before using it
)

# Create a session factory specifically for AsyncSessions
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False  # Prevents attributes from expiring after commit
)


# Async dependency to safely provision and yield database sessions per request
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

get_db_context = asynccontextmanager(get_db)


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),  # Generates UUID v4 in PostgreSQL
        default=uuid.uuid4                        # Python-side fallback generation
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=sa.func.now(),
        nullable=False
    )
