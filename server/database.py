import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

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
    max_overflow=20
)

# Create a session factory specifically for AsyncSessions
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False  # Prevents attributes from expiring after commit
)

Base = declarative_base()

# Async dependency to safely provision and yield database sessions per request
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
