from typing import Any, Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.roles import RoleMapping
from bot.database.repositories.base import BaseRepository

class RoleMappingRepository(BaseRepository[RoleMapping]):
    """Repository for RoleMapping models."""
    
    __slots__ = ()

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RoleMapping)

    async def get_by_guild(self, guild_id: int) -> Sequence[RoleMapping]:
        """Get all role mappings for a guild."""
        stmt = select(RoleMapping).where(RoleMapping.guild_id == guild_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_logical_name(self, guild_id: int, name: str) -> RoleMapping | None:
        """Get a role mapping by its logical name in a guild."""
        stmt = select(RoleMapping).where(
            RoleMapping.guild_id == guild_id, 
            RoleMapping.logical_name == name
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_discord_id(self, guild_id: int, discord_role_id: int) -> RoleMapping | None:
        """Get a role mapping by its discord role ID."""
        stmt = select(RoleMapping).where(
            RoleMapping.guild_id == guild_id,
            RoleMapping.discord_role_id == discord_role_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(self, guild_id: int, discord_role_id: int, logical_name: str, **kwargs: Any) -> RoleMapping:
        """Create or update a role mapping."""
        mapping = await self.get_by_discord_id(guild_id, discord_role_id)
        if not mapping:
            mapping = RoleMapping(
                guild_id=guild_id,
                discord_role_id=discord_role_id,
                logical_name=logical_name,
                **kwargs
            )
            self.session.add(mapping)
        else:
            mapping.logical_name = logical_name
            for key, value in kwargs.items():
                if hasattr(mapping, key):
                    setattr(mapping, key, value)
        
        await self.session.flush()
        return mapping

    async def delete_by_discord_id(self, guild_id: int, discord_role_id: int) -> bool:
        """Delete a role mapping by discord role ID."""
        stmt = delete(RoleMapping).where(
            RoleMapping.guild_id == guild_id,
            RoleMapping.discord_role_id == discord_role_id
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
