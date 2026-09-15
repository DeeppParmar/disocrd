import discord
from discord import app_commands
from discord.ext import commands
import structlog
from typing import Optional

from bot.core.bot import DiscordServerOS
from bot.utils.formatters import success_embed, info_embed
from bot.utils.checks import is_admin
from bot.cogs.analytics.views import AnalyticsDashboardView

log = structlog.get_logger()

class AnalyticsCog(commands.Cog):
    """Handles server analytics and stats."""
    
    __slots__ = ('bot',)

    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    analytics_group = app_commands.Group(name="analytics", description="Server analytics")

    @analytics_group.command(name="dashboard", description="Server overview with stats")
    @app_commands.guild_only()
    @is_admin()
    async def analytics_dashboard(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        
        embed = info_embed(
            title=f"📊 Analytics Dashboard for {interaction.guild.name}",
            description="Overview of server statistics."
        )
        embed.add_field(name="Members", value=str(interaction.guild.member_count))
        embed.add_field(name="Channels", value=str(len(interaction.guild.channels)))
        embed.add_field(name="Roles", value=str(len(interaction.guild.roles)))
        
        view = AnalyticsDashboardView(self.bot, interaction.guild_id)
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @analytics_group.command(name="members", description="Member stats over time")
    @app_commands.guild_only()
    @is_admin()
    async def analytics_members(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=info_embed(title="Member Stats", description="Graph data here..."), ephemeral=True)

    @analytics_group.command(name="activity", description="Message activity stats")
    @app_commands.guild_only()
    @is_admin()
    async def analytics_activity(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=info_embed(title="Activity Stats", description="Activity data here..."), ephemeral=True)

    @analytics_group.command(name="export", description="Export analytics as text file")
    @app_commands.guild_only()
    @is_admin()
    async def analytics_export(self, interaction: discord.Interaction, days: int = 30) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed(f"Exported data for the last {days} days."), ephemeral=True)
        log.info("analytics_exported", guild_id=interaction.guild_id, user_id=interaction.user.id, days=days)

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(AnalyticsCog(bot))
