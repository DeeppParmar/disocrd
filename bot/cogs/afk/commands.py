import discord
from discord import app_commands
from discord.ext import commands

from bot.core.bot import DiscordServerOS
from bot.services.afk_service import AFKService
from bot.utils.formatters import success_embed

class AFKCog(commands.GroupCog, group_name="afk"):
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot
        self.afk_service = AFKService(bot)

    @app_commands.command(name="set", description="Set your AFK status")
    @app_commands.guild_only()
    async def set_afk(self, interaction: discord.Interaction, reason: str = "AFK"):
        await self.afk_service.set_afk(interaction.guild_id, interaction.user.id, reason)
        await interaction.response.send_message(embed=success_embed(f"You are now AFK: {reason}"))
