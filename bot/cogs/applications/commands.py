import discord
from discord import app_commands
from discord.ext import commands
import structlog
from typing import Optional

from bot.core.bot import DiscordServerOS
from bot.utils.formatters import success_embed, info_embed
from bot.utils.checks import is_admin, is_staff
from bot.cogs.applications.views import ApplicationModal, ApplicationReviewView

log = structlog.get_logger()

class ApplicationsCog(commands.Cog):
    """Handles custom applications and forms."""
    
    __slots__ = ('bot',)

    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    @app_commands.command(name="apply", description="Submit an application")
    @app_commands.guild_only()
    async def apply(self, interaction: discord.Interaction, type: str) -> None:
        # We assume type is populated via autocomplete.
        # Here we'd fetch the DB config for this type.
        
        # Example dynamic fields from config
        form_fields = [
            {"label": "Why do you want to join?", "style": discord.TextStyle.paragraph, "required": True},
            {"label": "Previous experience?", "style": discord.TextStyle.paragraph, "required": True}
        ]
        
        modal = ApplicationModal(bot=self.bot, app_type=type, fields=form_fields)
        await interaction.response.send_modal(modal)

    @apply.autocomplete('type')
    async def apply_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        # Usually from DB
        types = ['staff', 'creator', 'partner']
        return [app_commands.Choice(name=t, value=t) for t in types if current.lower() in t.lower()][:25]

    app_admin_group = app_commands.Group(name="applications", description="Manage applications")

    @app_admin_group.command(name="setup", description="Create an application configuration")
    @app_commands.guild_only()
    @is_admin()
    async def app_setup(
        self, 
        interaction: discord.Interaction, 
        type: str, 
        name: str, 
        channel: discord.TextChannel, 
        role: Optional[discord.Role] = None
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        # Save config to DB
        await interaction.followup.send(embed=success_embed(f"Application type `{type}` configured to send to {channel.mention}."), ephemeral=True)

    @app_admin_group.command(name="list", description="List submitted applications")
    @app_commands.choices(status=[
        app_commands.Choice(name="Pending", value="pending"),
        app_commands.Choice(name="Approved", value="approved"),
        app_commands.Choice(name="Rejected", value="rejected")
    ])
    @app_commands.guild_only()
    @is_staff()
    async def app_list(self, interaction: discord.Interaction, status: Optional[str] = None) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=info_embed("Applications", "List of applications..."), ephemeral=True)

    @app_admin_group.command(name="review", description="Review an application")
    @app_commands.guild_only()
    @is_staff()
    async def app_review(self, interaction: discord.Interaction, id: int) -> None:
        await interaction.response.defer(ephemeral=True)
        
        embed = info_embed(title=f"Application #{id}", description="Details of application...")
        view = ApplicationReviewView(self.bot, app_id=id)
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(ApplicationsCog(bot))
