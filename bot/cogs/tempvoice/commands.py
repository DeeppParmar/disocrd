import discord
from discord import app_commands
from discord.ext import commands
import structlog

from bot.core.bot import DiscordServerOS
from bot.utils.formatters import success_embed, error_embed, info_embed
from bot.utils.checks import is_admin
from bot.cogs.tempvoice.views import TempVoiceControlView

log = structlog.get_logger()

class TempVoiceCog(commands.Cog):
    """Handles temporary voice channels."""
    
    __slots__ = ('bot',)

    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    tempvoice_group = app_commands.Group(name="tempvoice", description="Temp voice commands")

    @tempvoice_group.command(name="setup", description="Configure temp voice in a category")
    @app_commands.guild_only()
    @is_admin()
    async def tempvoice_setup(self, interaction: discord.Interaction, category: discord.CategoryChannel) -> None:
        await interaction.response.defer(ephemeral=True)
        
        # Create Join to Create channel
        try:
            channel = await category.create_voice_channel("➕ Join to Create")
            # Save to DB
            log.info("tempvoice_setup", guild_id=interaction.guild_id, category_id=category.id, channel_id=channel.id)
            await interaction.followup.send(embed=success_embed(f"Setup complete! Voice channel {channel.mention} created."), ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send(embed=error_embed("Missing permissions to create channels."), ephemeral=True)

    @tempvoice_group.command(name="limit", description="Set user limit on your temp channel")
    @app_commands.guild_only()
    async def tempvoice_limit(self, interaction: discord.Interaction, limit: app_commands.Range[int, 0, 99]) -> None:
        await interaction.response.defer(ephemeral=True)
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.followup.send(embed=error_embed("You are not in a voice channel."), ephemeral=True)
        
        await interaction.user.voice.channel.edit(user_limit=limit)
        await interaction.followup.send(embed=success_embed(f"Channel limit set to {limit}."), ephemeral=True)

    @tempvoice_group.command(name="name", description="Rename your temp channel")
    @app_commands.guild_only()
    async def tempvoice_name(self, interaction: discord.Interaction, name: str) -> None:
        await interaction.response.defer(ephemeral=True)
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.followup.send(embed=error_embed("You are not in a voice channel."), ephemeral=True)
        
        await interaction.user.voice.channel.edit(name=name)
        await interaction.followup.send(embed=success_embed(f"Channel renamed to {name}."), ephemeral=True)

    @tempvoice_group.command(name="lock", description="Lock your temp channel")
    @app_commands.guild_only()
    async def tempvoice_lock(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.followup.send(embed=error_embed("You are not in a voice channel."), ephemeral=True)
        
        channel = interaction.user.voice.channel
        await channel.set_permissions(interaction.guild.default_role, connect=False)
        await interaction.followup.send(embed=success_embed("Channel locked."), ephemeral=True)

    @tempvoice_group.command(name="unlock", description="Unlock your temp channel")
    @app_commands.guild_only()
    async def tempvoice_unlock(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.followup.send(embed=error_embed("You are not in a voice channel."), ephemeral=True)
        
        channel = interaction.user.voice.channel
        await channel.set_permissions(interaction.guild.default_role, connect=True)
        await interaction.followup.send(embed=success_embed("Channel unlocked."), ephemeral=True)

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(TempVoiceCog(bot))
