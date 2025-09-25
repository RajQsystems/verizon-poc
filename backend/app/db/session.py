from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.app.core.config import settings


DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.DATABASE_USERNAME,
    password=settings.DATABASE_PASSWORD,
    host=settings.DATABASE_HOST,
    database=settings.DATABASE_NAME,
    port=settings.DATABASE_PORT,
)

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
