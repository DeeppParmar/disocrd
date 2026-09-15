import discord
from discord import app_commands
from discord.ext import commands
import structlog
from typing import Optional

from bot.core.bot import DiscordServerOS
from bot.utils.formatters import success_embed, error_embed
from bot.utils.checks import is_moderator
from bot.cogs.cleanup.views import PurgeConfirmView

log = structlog.get_logger()

class CleanupCog(commands.Cog):
    """Handles channel cleanup and purging."""
    
    __slots__ = ('bot',)

    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    purge_group = app_commands.Group(name="purge", description="Purge messages")

    @purge_group.command(name="count", description="Delete recent messages")
    @app_commands.guild_only()
    @is_moderator()
    async def purge_count(self, interaction: discord.Interaction, count: app_commands.Range[int, 1, 100]) -> None:
        await self._handle_purge(interaction, count)

    @purge_group.command(name="user", description="Delete messages from a specific user")
    @app_commands.guild_only()
    @is_moderator()
    async def purge_user(self, interaction: discord.Interaction, user: discord.Member, count: app_commands.Range[int, 1, 100]) -> None:
        def check(m: discord.Message) -> bool:
            return m.author.id == user.id
        await self._handle_purge(interaction, count, check=check)

    @purge_group.command(name="bots", description="Delete messages from bots")
    @app_commands.guild_only()
    @is_moderator()
    async def purge_bots(self, interaction: discord.Interaction, count: app_commands.Range[int, 1, 100]) -> None:
        def check(m: discord.Message) -> bool:
            return m.author.bot
        await self._handle_purge(interaction, count, check=check)

    @purge_group.command(name="links", description="Delete messages containing URLs")
    @app_commands.guild_only()
    @is_moderator()
    async def purge_links(self, interaction: discord.Interaction, count: app_commands.Range[int, 1, 100]) -> None:
        def check(m: discord.Message) -> bool:
            return "http://" in m.content or "https://" in m.content
        await self._handle_purge(interaction, count, check=check)

    @purge_group.command(name="attachments", description="Delete messages with attachments")
    @app_commands.guild_only()
    @is_moderator()
    async def purge_attachments(self, interaction: discord.Interaction, count: app_commands.Range[int, 1, 100]) -> None:
        def check(m: discord.Message) -> bool:
            return len(m.attachments) > 0
        await self._handle_purge(interaction, count, check=check)

    async def _handle_purge(self, interaction: discord.Interaction, count: int, check=None) -> None:
        if count > 50:
            view = PurgeConfirmView(self.bot, channel=interaction.channel, count=count, check=check)
            await interaction.response.send_message(
                embed=error_embed(f"Are you sure you want to delete {count} messages?"),
                view=view,
                ephemeral=True
            )
        else:
            await interaction.response.defer(ephemeral=True)
            deleted = await interaction.channel.purge(limit=count, check=check)
            await interaction.followup.send(embed=success_embed(f"Deleted {len(deleted)} messages."), ephemeral=True)
            log.info("channel_purged", channel_id=interaction.channel_id, count=len(deleted), user_id=interaction.user.id)

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(CleanupCog(bot))
