"""Security event listeners for raid detection and threat monitoring."""

import time
from collections import defaultdict

import discord
from discord.ext import commands
import structlog

from bot.core.bot import DiscordServerOS
from bot.core.constants import Colors
from bot.services.security_service import SecurityService
from bot.utils.formatters import warning_embed, error_embed

logger = structlog.get_logger(__name__)


class SecurityListenersCog(commands.Cog):
    """Monitors security-relevant events in real-time."""

    __slots__ = ("bot", "security", "_channel_deletes", "_role_deletes")

    def __init__(self, bot: DiscordServerOS) -> None:
        self.bot = bot
        self.security = SecurityService(bot)
        # Track rapid deletions: guild_id -> list of timestamps
        self._channel_deletes: dict[int, list[float]] = defaultdict(list)
        self._role_deletes: dict[int, list[float]] = defaultdict(list)

    def _check_rapid_action(self, tracker: dict[int, list[float]], guild_id: int, threshold: int = 3, window: float = 10.0) -> bool:
        """Check if actions are happening too rapidly (potential attack)."""
        now = time.time()
        tracker[guild_id] = [t for t in tracker[guild_id] if now - t < window]
        tracker[guild_id].append(now)
        return len(tracker[guild_id]) >= threshold

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Detect raid patterns and suspicious accounts."""
        guild = member.guild
        is_raid = await self.security.check_raid(guild.id, time.time())

        if is_raid:
            logger.warning("Raid detected", guild_id=guild.id, member_id=member.id)
            await self.security.activate_lockdown(guild, "Auto-lockdown: raid detected", self.bot.user.id)
            await self._alert_staff(guild, error_embed(
                "🚨 Raid Detected",
                f"Unusual join spike detected ({len(self.security.join_tracker.get(guild.id, []))} joins in 30s).\n"
                f"**Auto-lockdown activated.** Use `/security unlock` to deactivate."
            ))

        # Check account age
        account_age_hours = (discord.utils.utcnow() - member.created_at).total_seconds() / 3600
        if account_age_hours < 24:
            logger.info("New account joined", guild_id=guild.id, member_id=member.id, age_hours=round(account_age_hours, 1))
            await self._alert_staff(guild, warning_embed(
                "⚠️ New Account Alert",
                f"{member.mention} ({member}) joined with an account created **{round(account_age_hours, 1)} hours ago**."
            ))

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        """Track leave spikes that may indicate a raid or mass-ban."""
        pass  # Leave tracking handled by analytics; raid detection focuses on joins

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        """Alert on rapid channel deletions (potential nuke attack)."""
        guild = channel.guild
        if self._check_rapid_action(self._channel_deletes, guild.id, threshold=3, window=10.0):
            logger.critical("Rapid channel deletion detected", guild_id=guild.id, channel=channel.name)
            await self.security.activate_lockdown(guild, "Auto-lockdown: mass channel deletion detected", self.bot.user.id)
            await self._alert_staff(guild, error_embed(
                "🚨 Mass Channel Deletion",
                f"Multiple channels deleted rapidly. Auto-lockdown activated.\n"
                f"Latest deleted: **#{channel.name}**\nCheck audit log immediately."
            ))

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role) -> None:
        """Alert on rapid role deletions (potential nuke attack)."""
        guild = role.guild
        if self._check_rapid_action(self._role_deletes, guild.id, threshold=3, window=10.0):
            logger.critical("Rapid role deletion detected", guild_id=guild.id, role=role.name)
            await self._alert_staff(guild, error_embed(
                "🚨 Mass Role Deletion",
                f"Multiple roles deleted rapidly.\nLatest deleted: **@{role.name}**\nCheck audit log immediately."
            ))

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel: discord.abc.GuildChannel) -> None:
        """Alert on webhook changes (potential token theft vector)."""
        await self._alert_staff(channel.guild, warning_embed(
            "🔗 Webhook Updated",
            f"Webhooks were modified in {channel.mention}.\nCheck audit log for details."
        ))

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        """Detect dangerous permission grants (Administrator role)."""
        if before.roles == after.roles:
            return

        new_roles = set(after.roles) - set(before.roles)
        for role in new_roles:
            if role.permissions.administrator:
                logger.warning(
                    "Administrator role granted",
                    guild_id=after.guild.id,
                    target_id=after.id,
                    role_name=role.name,
                )
                await self._alert_staff(after.guild, error_embed(
                    "🔴 Administrator Role Granted",
                    f"**{after}** was granted the **@{role.name}** role (has Administrator permission).\n"
                    f"If this was not intentional, remove it immediately."
                ))

    async def _alert_staff(self, guild: discord.Guild, embed: discord.Embed) -> None:
        """Send an alert embed to the security log channel."""
        from bot.database.repositories.guild_repo import GuildRepository
        async with self.bot.db.session() as session:
            repo = GuildRepository(session)
            config = await repo.get_config(guild.id)
            if config and config.security_log_channel_id:
                channel = guild.get_channel(config.security_log_channel_id)
                if channel and isinstance(channel, discord.TextChannel):
                    try:
                        await channel.send(embed=embed)
                    except discord.HTTPException:
                        pass


async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(SecurityListenersCog(bot))
