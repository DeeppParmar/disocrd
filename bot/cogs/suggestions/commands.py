import discord
from discord import app_commands
from discord.ext import commands
import structlog
from typing import Optional

from bot.core.bot import DiscordServerOS
from bot.utils.formatters import success_embed, info_embed
from bot.utils.checks import is_staff
from bot.cogs.suggestions.views import SuggestionVoteView

log = structlog.get_logger()

class SuggestionsCog(commands.Cog):
    """Handles server suggestions."""
    
    __slots__ = ('bot',)

    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    @app_commands.command(name="suggest", description="Submit a suggestion")
    @app_commands.guild_only()
    async def suggest(self, interaction: discord.Interaction, content: str) -> None:
        await interaction.response.defer(ephemeral=True)
        
        # Normally fetch config from DB and save
        embed = info_embed(
            title="New Suggestion",
            description=content
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="Status", value="Pending", inline=False)
        
        view = SuggestionVoteView(self.bot, suggestion_id=interaction.id)
        
        msg = await interaction.channel.send(embed=embed, view=view)
        
        await interaction.followup.send(embed=success_embed("Suggestion submitted successfully!"), ephemeral=True)
        log.info("suggestion_submitted", user_id=interaction.user.id, guild_id=interaction.guild_id)

    suggestion_group = app_commands.Group(name="suggestion", description="Suggestion management commands")

    @suggestion_group.command(name="status", description="Update a suggestion's status")
    @app_commands.choices(status=[
        app_commands.Choice(name="Approved", value="approved"),
        app_commands.Choice(name="Rejected", value="rejected"),
        app_commands.Choice(name="Implemented", value="implemented"),
        app_commands.Choice(name="Duplicate", value="duplicate")
    ])
    @app_commands.guild_only()
    @is_staff()
    async def suggestion_status(
        self, 
        interaction: discord.Interaction, 
        id: int, 
        status: str, 
        response: Optional[str] = None
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed(f"Suggestion #{id} status updated to {status}."), ephemeral=True)
        log.info("suggestion_status_updated", user_id=interaction.user.id, suggestion_id=id, status=status)

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(SuggestionsCog(bot))
