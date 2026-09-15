from typing import Any, Generic, Sequence, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.base import Base

T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    """Base repository class providing generic CRUD operations."""
    
    __slots__ = ("session", "model_class")

    def __init__(self, session: AsyncSession, model_class: Type[T]) -> None:
        """Initialize repository with session and model class."""
        self.session = session
        self.model_class = model_class

    async def get_by_id(self, id: Any) -> T | None:
        """Get an entity by its primary key."""
        return await self.session.get(self.model_class, id)

    async def get_all(self, **filters: Any) -> Sequence[T]:
        """Get all entities matching the provided filters."""
        stmt = select(self.model_class)
        for key, value in filters.items():
            stmt = stmt.where(getattr(self.model_class, key) == value)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, entity: T) -> T:
        """Create a new entity."""
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, entity: T) -> T:
        """Update an existing entity."""
        await self.session.flush()
        return entity

    async def delete(self, id: Any) -> bool:
        """Delete an entity by its primary key."""
        entity = await self.get_by_id(id)
        if entity:
            await self.session.delete(entity)
            await self.session.flush()
            return True
        return False
