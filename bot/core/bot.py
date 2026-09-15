"""Custom bot implementation."""

from pathlib import Path
from typing import Any

import discord
from discord.ext import commands
import structlog

from bot.config.settings import Settings
from bot.config.intents import get_intents
from bot.core.tree import BotCommandTree

logger = structlog.get_logger(__name__)


class DiscordServerOS(commands.AutoShardedBot):
    """The core bot class for Discord Server OS.
    
    Attributes:
        settings (Settings): The application configuration.
        db (Any): The database manager.
        redis (Any): The Redis client.
    """
    
    __slots__ = ("settings", "db", "redis")
    
    def __init__(
        self,
        settings: Settings,
        db: Any,
        redis: Any
    ) -> None:
        """Initialize the bot.
        
        Args:
            settings: Application configuration.
            db: Database manager instance.
            redis: Redis client instance.
        """
        self.settings = settings
        self.db = db
        self.redis = redis
        
        super().__init__(
            command_prefix="!",
            intents=get_intents(),
            shard_count=self.settings.SHARD_COUNT,
            tree_cls=BotCommandTree,
            help_command=None
        )

    async def setup_hook(self) -> None:
        """Hook called before the bot starts running."""
        cogs_dir = Path(__file__).parent.parent / "cogs"
        if cogs_dir.exists():
            for filepath in cogs_dir.rglob("*.py"):
                if filepath.name.startswith("__"):
                    continue
                rel_path = filepath.relative_to(cogs_dir.parent.parent)
                module_name = ".".join(rel_path.with_suffix("").parts)
                try:
                    await self.load_extension(module_name)
                    logger.info("Loaded cog", module=module_name)
                except Exception as e:
                    logger.exception("Failed to load cog", module=module_name, error=e)
                    
        if self.settings.DEV_GUILD_ID:
            guild = discord.Object(id=self.settings.DEV_GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info("Synced commands to development guild", guild_id=self.settings.DEV_GUILD_ID)
        else:
            await self.tree.sync()
            logger.info("Synced commands globally")

    async def on_ready(self) -> None:
        """Event fired when the bot is ready."""
        logger.info(
            "Bot is ready",
            user=str(self.user),
            user_id=self.user.id if self.user else None,
            shard_count=self.shard_count,
            guild_count=len(self.guilds)
        )

    async def close(self) -> None:
        """Gracefully shutdown the bot and close connections."""
        logger.info("Shutting down bot...")
        
        if hasattr(self.db, "dispose"):
            await self.db.dispose()
            
        if hasattr(self.redis, "aclose"):
            await self.redis.aclose()
        elif hasattr(self.redis, "close"):
            await self.redis.close()
            
        await super().close()
