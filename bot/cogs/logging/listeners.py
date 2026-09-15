"""Event loggers for all auditable Discord events."""

import discord
from discord.ext import commands
import structlog

from bot.core.bot import DiscordServerOS
from bot.core.constants import Colors, LogCategory
from bot.services.logging_service import LoggingService

logger = structlog.get_logger(__name__)


class LoggingListenersCog(commands.Cog):
    """Captures and logs all auditable events to configured channels."""

    __slots__ = ("bot", "log_service")

    def __init__(self, bot: DiscordServerOS) -> None:
        self.bot = bot
        self.log_service = LoggingService(bot)

    def _is_self(self, user_id: int) -> bool:
        """Check if action was performed by the bot itself."""
        return user_id == self.bot.user.id if self.bot.user else False

    # ── Messages ──────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if not message.guild or message.author.bot:
            return
        await self.log_service.log_event(
            guild_id=message.guild.id,
            event_type="message_delete",
            category=LogCategory.MESSAGES.name,
            actor_id=message.author.id,
            channel_id=message.channel.id,
            details={"content": message.content[:500] if message.content else "", "author": str(message.author)},
        )

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: list[discord.Message]) -> None:
        if not messages or not messages[0].guild:
            return
        guild = messages[0].guild
        await self.log_service.log_event(
            guild_id=guild.id,
            event_type="bulk_message_delete",
            category=LogCategory.MESSAGES.name,
            channel_id=messages[0].channel.id,
            details={"count": len(messages)},
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if not after.guild or after.author.bot or before.content == after.content:
            return
        await self.log_service.log_event(
            guild_id=after.guild.id,
            event_type="message_edit",
            category=LogCategory.MESSAGES.name,
            actor_id=after.author.id,
            channel_id=after.channel.id,
            details={"before": before.content[:300], "after": after.content[:300]},
        )

    # ── Members ───────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        await self.log_service.log_event(
            guild_id=member.guild.id,
            event_type="member_join",
            category=LogCategory.MEMBERS.name,
            target_id=member.id,
            details={"account_created": member.created_at.isoformat(), "member_count": member.guild.member_count},
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        await self.log_service.log_event(
            guild_id=member.guild.id,
            event_type="member_leave",
            category=LogCategory.MEMBERS.name,
            target_id=member.id,
            details={"roles": [r.name for r in member.roles if r.id != member.guild.id]},
        )

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        if before.nick != after.nick:
            await self.log_service.log_event(
                guild_id=after.guild.id,
                event_type="nickname_change",
                category=LogCategory.MEMBERS.name,
                target_id=after.id,
                details={"before": before.nick, "after": after.nick},
            )

        added_roles = set(after.roles) - set(before.roles)
        removed_roles = set(before.roles) - set(after.roles)
        if added_roles or removed_roles:
            await self.log_service.log_event(
                guild_id=after.guild.id,
                event_type="role_change",
                category=LogCategory.ROLES.name,
                target_id=after.id,
                details={
                    "added": [r.name for r in added_roles],
                    "removed": [r.name for r in removed_roles],
                },
            )

    # ── Roles ─────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role) -> None:
        await self.log_service.log_event(
            guild_id=role.guild.id,
            event_type="role_create",
            category=LogCategory.ROLES.name,
            details={"name": role.name, "color": str(role.color), "permissions": role.permissions.value},
        )

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role) -> None:
        changes = {}
        if before.name != after.name:
            changes["name"] = {"before": before.name, "after": after.name}
        if before.permissions != after.permissions:
            changes["permissions"] = {"before": before.permissions.value, "after": after.permissions.value}
        if before.color != after.color:
            changes["color"] = {"before": str(before.color), "after": str(after.color)}
        if changes:
            await self.log_service.log_event(
                guild_id=after.guild.id,
                event_type="role_update",
                category=LogCategory.ROLES.name,
                details={"role": after.name, "changes": changes},
            )

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role) -> None:
        await self.log_service.log_event(
            guild_id=role.guild.id,
            event_type="role_delete",
            category=LogCategory.ROLES.name,
            details={"name": role.name, "member_count": len(role.members)},
        )

    # ── Channels ──────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel) -> None:
        await self.log_service.log_event(
            guild_id=channel.guild.id,
            event_type="channel_create",
            category=LogCategory.CHANNELS.name,
            channel_id=channel.id,
            details={"name": channel.name, "type": str(channel.type)},
        )

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel) -> None:
        changes = {}
        if before.name != after.name:
            changes["name"] = {"before": before.name, "after": after.name}
        if hasattr(before, "topic") and hasattr(after, "topic") and before.topic != after.topic:
            changes["topic"] = {"before": getattr(before, "topic", ""), "after": getattr(after, "topic", "")}
        if changes:
            await self.log_service.log_event(
                guild_id=after.guild.id,
                event_type="channel_update",
                category=LogCategory.CHANNELS.name,
                channel_id=after.id,
                details={"changes": changes},
            )

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        await self.log_service.log_event(
            guild_id=channel.guild.id,
            event_type="channel_delete",
            category=LogCategory.CHANNELS.name,
            details={"name": channel.name, "type": str(channel.type)},
        )

    # ── Invites ───────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite) -> None:
        if invite.guild:
            await self.log_service.log_event(
                guild_id=invite.guild.id,
                event_type="invite_create",
                category=LogCategory.INVITES.name,
                actor_id=invite.inviter.id if invite.inviter else None,
                details={"code": invite.code, "max_uses": invite.max_uses, "max_age": invite.max_age},
            )

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite) -> None:
        if invite.guild:
            await self.log_service.log_event(
                guild_id=invite.guild.id,
                event_type="invite_delete",
                category=LogCategory.INVITES.name,
                details={"code": invite.code, "uses": invite.uses},
            )

    # ── Webhooks ──────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel: discord.abc.GuildChannel) -> None:
        await self.log_service.log_event(
            guild_id=channel.guild.id,
            event_type="webhook_update",
            category=LogCategory.WEBHOOKS.name,
            channel_id=channel.id,
            details={"channel": channel.name},
        )

    # ── AutoMod ───────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_automod_action(self, execution: discord.AutoModAction) -> None:
        await self.log_service.log_event(
            guild_id=execution.guild_id,
            event_type="automod_action",
            category=LogCategory.AUTOMOD.name,
            target_id=execution.member_id,
            channel_id=execution.channel_id,
            details={
                "rule_id": execution.rule_id,
                "action_type": str(execution.action.type),
                "content": execution.content[:200] if execution.content else "",
                "matched_keyword": execution.matched_keyword or "",
            },
        )


async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(LoggingListenersCog(bot))
