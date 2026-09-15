import discord
from discord import app_commands
from discord.ext import commands
import structlog

from bot.core.bot import DiscordServerOS
from bot.utils.formatters import success_embed, error_embed
from bot.utils.checks import is_admin

logger = structlog.get_logger()

class WelcomeMessageModal(discord.ui.Modal, title="Set Welcome Message"):
    template = discord.ui.TextInput(
        label="Message Template",
        style=discord.TextStyle.paragraph,
        placeholder="Welcome {user} to {server}! You are member #{member_count}.",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=success_embed("Welcome message template updated."),
            ephemeral=True
        )

class WelcomeCog(commands.Cog):
    """Welcome system commands."""
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    group = app_commands.Group(name="welcome", description="Welcome commands", guild_only=True)

    @group.command(name="channel")
    @is_admin()
    async def channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Set the welcome channel."""
        await interaction.response.send_message(
            embed=success_embed(f"Welcome channel set to {channel.mention}"),
            ephemeral=True
        )

    @group.command(name="message")
    @is_admin()
    async def message(self, interaction: discord.Interaction):
        """Set the welcome message template."""
        await interaction.response.send_modal(WelcomeMessageModal())

    @group.command(name="test")
    @is_admin()
    async def test(self, interaction: discord.Interaction):
        """Send a test welcome message."""
        await interaction.response.send_message(
            f"Welcome {interaction.user.mention} to {interaction.guild.name}! You are member #{interaction.guild.member_count}.",
            ephemeral=True
        )

    @group.command(name="toggle")
    @is_admin()
    async def toggle(self, interaction: discord.Interaction):
        """Enable or disable welcome messages."""
        await interaction.response.send_message(
            embed=success_embed("Toggled welcome messages."),
            ephemeral=True
        )

async def setup(bot: DiscordServerOS):
    await bot.add_cog(WelcomeCog(bot))
