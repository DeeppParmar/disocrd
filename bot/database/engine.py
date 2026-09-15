from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connection and session creation."""
    
    __slots__ = ("engine", "session_factory")

    def __init__(self, database_url: str) -> None:
        """Initialize the database manager with Supabase-optimized settings.
        
        Args:
            database_url: The asyncpg connection string.
        """
        self.engine: AsyncEngine = create_async_engine(
            database_url,
            pool_size=10,
            max_overflow=5,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
            connect_args={"ssl": "require"},
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide a transactional scope around a series of operations."""
        session: AsyncSession = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Database transaction error: {e}", exc_info=True)
            await session.rollback()
            raise
        finally:
            await session.close()

    async def dispose(self) -> None:
        """Dispose of the connection pool."""
        if self.engine:
            await self.engine.dispose()
