from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.configs import settings

async_engine = create_async_engine(
    url=settings.db_url,
    echo=settings.debug,
)
async_session = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
)
