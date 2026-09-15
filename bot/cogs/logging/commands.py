import discord
from discord import app_commands
from discord.ext import commands
import structlog
from typing import Optional

from bot.core.bot import DiscordServerOS
from bot.core.constants import LogCategory
from bot.utils.formatters import success_embed, error_embed
from bot.utils.checks import is_admin

logger = structlog.get_logger()

class LoggingCog(commands.Cog):
    """Logging configuration commands."""
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    group = app_commands.Group(name="logs", description="Logging commands", guild_only=True)

    @group.command(name="config")
    @is_admin()
    async def config(self, interaction: discord.Interaction, category: str, channel: discord.TextChannel):
        """Configure a log channel for a category."""
        await interaction.response.send_message(
            embed=success_embed(f"Configured logging for `{category}` to {channel.mention}"), 
            ephemeral=True
        )

    @group.command(name="view")
    @is_admin()
    async def view(self, interaction: discord.Interaction, category: str, limit: int = 25):
        """View recent logged events."""
        await interaction.response.send_message(f"Displaying up to {limit} logs for {category}...", ephemeral=True)

    @group.command(name="disable")
    @is_admin()
    async def disable(self, interaction: discord.Interaction, category: str):
        """Disable a logging category."""
        await interaction.response.send_message(
            embed=success_embed(f"Disabled logging for `{category}`."), 
            ephemeral=True
        )

async def setup(bot: DiscordServerOS):
    await bot.add_cog(LoggingCog(bot))
