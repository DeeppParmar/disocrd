from __future__ import annotations

import discord
from discord.ext import commands
import structlog

from bot.core.bot import DiscordServerOS

logger = structlog.get_logger(__name__)

class ModerationListeners(commands.Cog):
    def __init__(self, bot: DiscordServerOS) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User | discord.Member) -> None:
        """Log member bans."""
        logger.info("member_banned", guild_id=guild.id, user_id=user.id)
        # Fetch audit log entry to get reason and moderator
        # Log to mod log channel

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User) -> None:
        """Log member unbans."""
        logger.info("member_unbanned", guild_id=guild.id, user_id=user.id)
        # Fetch audit log entry
        # Log to mod log channel

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        """Detect timeout changes."""
        if before.timed_out_until != after.timed_out_until:
            if after.timed_out_until is not None:
                logger.info("member_timed_out", guild_id=after.guild.id, user_id=after.id)
                # Fetch audit log, create case if not exists
            else:
                logger.info("member_timeout_removed", guild_id=after.guild.id, user_id=after.id)

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(ModerationListeners(bot))
