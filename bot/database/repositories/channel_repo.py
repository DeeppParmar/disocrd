from typing import Any, Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.channels import ChannelMapping
from bot.database.repositories.base import BaseRepository

class ChannelMappingRepository(BaseRepository[ChannelMapping]):
    """Repository for ChannelMapping models."""
    
    __slots__ = ()

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ChannelMapping)

    async def get_by_guild(self, guild_id: int) -> Sequence[ChannelMapping]:
        """Get all channel mappings for a guild."""
        stmt = select(ChannelMapping).where(ChannelMapping.guild_id == guild_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_logical_name(self, guild_id: int, name: str) -> ChannelMapping | None:
        """Get a channel mapping by its logical name in a guild."""
        stmt = select(ChannelMapping).where(
            ChannelMapping.guild_id == guild_id, 
            ChannelMapping.logical_name == name
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_discord_id(self, guild_id: int, discord_channel_id: int) -> ChannelMapping | None:
        """Get a channel mapping by its discord channel ID."""
        stmt = select(ChannelMapping).where(
            ChannelMapping.guild_id == guild_id,
            ChannelMapping.discord_channel_id == discord_channel_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(self, guild_id: int, discord_channel_id: int, logical_name: str, **kwargs: Any) -> ChannelMapping:
        """Create or update a channel mapping."""
        mapping = await self.get_by_discord_id(guild_id, discord_channel_id)
        if not mapping:
            mapping = ChannelMapping(
                guild_id=guild_id,
                discord_channel_id=discord_channel_id,
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

    async def delete_by_discord_id(self, guild_id: int, discord_channel_id: int) -> bool:
        """Delete a channel mapping by discord channel ID."""
        stmt = delete(ChannelMapping).where(
            ChannelMapping.guild_id == guild_id,
            ChannelMapping.discord_channel_id == discord_channel_id
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
