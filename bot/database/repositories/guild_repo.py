from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from bot.database.models.guild import Guild, GuildConfig
from bot.database.repositories.base import BaseRepository

class GuildRepository(BaseRepository[Guild]):
    """Repository for Guild and GuildConfig models."""
    
    __slots__ = ()

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Guild)

    async def get_or_create(self, guild_id: int) -> Guild:
        """Get a guild by ID, creating it if it doesn't exist."""
        guild = await self.get_by_id(guild_id)
        if not guild:
            guild = Guild(guild_id=guild_id)
            await self.create(guild)
        return guild

    async def get_config(self, guild_id: int) -> GuildConfig | None:
        """Get the configuration for a guild."""
        return await self.session.get(GuildConfig, guild_id)

    async def get_or_create_config(self, guild_id: int) -> GuildConfig:
        """Get the config for a guild, creating it if it doesn't exist."""
        config = await self.get_config(guild_id)
        if not config:
            await self.get_or_create(guild_id)  # Ensure guild exists
            config = GuildConfig(guild_id=guild_id)
            self.session.add(config)
            await self.session.flush()
        return config

    async def update_config(self, guild_id: int, **kwargs: Any) -> GuildConfig:
        """Update a guild's configuration."""
        config = await self.get_or_create_config(guild_id)
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        await self.session.flush()
        return config

    async def set_feature(self, guild_id: int, feature: str, enabled: bool) -> GuildConfig:
        """Enable or disable a specific feature for a guild."""
        config = await self.get_or_create_config(guild_id)
        # We must create a new dict for SQLAlchemy to detect the change in JSONB
        features = dict(config.features_enabled)
        features[feature] = enabled
        config.features_enabled = features
        await self.session.flush()
        return config
