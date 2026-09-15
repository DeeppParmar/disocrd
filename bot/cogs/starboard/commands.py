import discord
from discord import app_commands
from discord.ext import commands

from bot.core.bot import DiscordServerOS
from bot.services.starboard_service import StarboardService
from bot.utils.formatters import success_embed, error_embed, info_embed
from bot.utils.checks import is_admin

class StarboardCog(commands.GroupCog, group_name="starboard"):
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot
        self.starboard_service = StarboardService(bot)

    @app_commands.command(name="setup", description="Configure the starboard")
    @app_commands.guild_only()
    @is_admin()
    async def setup_starboard(
        self, 
        interaction: discord.Interaction, 
        channel: discord.TextChannel, 
        emoji: str = '⭐', 
        threshold: int = 3
    ):
        await self.starboard_service.setup(interaction.guild_id, channel.id, emoji, threshold)
        await interaction.response.send_message(embed=success_embed(f"Starboard configured in {channel.mention} with {emoji} and threshold {threshold}."))

    @app_commands.command(name="config", description="Update starboard configuration")
    @app_commands.guild_only()
    @is_admin()
    async def config_starboard(
        self, 
        interaction: discord.Interaction, 
        threshold: int = None, 
        emoji: str = None, 
        self_star: bool = None
    ):
        config = await self.starboard_service.get_config(interaction.guild_id)
        if not config:
            await interaction.response.send_message(embed=error_embed("Starboard is not set up."), ephemeral=True)
            return

        t = threshold if threshold is not None else config.threshold
        e = emoji if emoji is not None else config.emoji
        s = self_star if self_star is not None else config.self_star

        await self.starboard_service.setup(interaction.guild_id, config.channel_id, e, t)
        
        # update self star manually
        async with self.bot.db.session() as session:
            config.self_star = s
            await session.commit()

        await interaction.response.send_message(embed=success_embed("Starboard configuration updated."))

    @app_commands.command(name="toggle", description="Enable/disable the starboard")
    @app_commands.guild_only()
    @is_admin()
    async def toggle_starboard(self, interaction: discord.Interaction):
        config = await self.starboard_service.get_config(interaction.guild_id)
        if not config:
            await interaction.response.send_message(embed=error_embed("Starboard is not set up."), ephemeral=True)
            return

        async with self.bot.db.session() as session:
            config.enabled = not config.enabled
            await session.commit()
            
        status = "enabled" if config.enabled else "disabled"
        await interaction.response.send_message(embed=success_embed(f"Starboard is now {status}."))
