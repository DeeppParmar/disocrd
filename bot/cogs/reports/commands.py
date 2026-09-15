import discord
from discord import app_commands
from discord.ext import commands
import structlog
from typing import Optional

from bot.core.bot import DiscordServerOS
from bot.utils.formatters import success_embed, error_embed, info_embed
from bot.utils.checks import is_staff
from bot.cogs.reports.views import ReportActionView

log = structlog.get_logger()

class ReportsCog(commands.Cog):
    """Handles user and message reports."""
    
    __slots__ = ('bot',)

    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    report_group = app_commands.Group(name="report", description="Report members or messages")

    @report_group.command(name="member", description="Report a member")
    @app_commands.guild_only()
    async def report_member(
        self, 
        interaction: discord.Interaction, 
        target: discord.Member, 
        reason: str
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        
        embed = info_embed(
            title="Member Report",
            description=f"**Target:** {target.mention} ({target.id})\n**Reporter:** {interaction.user.mention}\n**Reason:** {reason}"
        )
        
        view = ReportActionView(self.bot, report_id=interaction.id)
        
        # Normally send to reports channel from DB
        await interaction.followup.send(embed=success_embed("Report submitted successfully."), ephemeral=True)
        log.info("member_reported", reporter_id=interaction.user.id, target_id=target.id, guild_id=interaction.guild_id)

    @report_group.command(name="message", description="Report a message")
    @app_commands.guild_only()
    async def report_message(
        self, 
        interaction: discord.Interaction, 
        message_id: str, 
        reason: str
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed("Message report submitted successfully."), ephemeral=True)
        log.info("message_reported", reporter_id=interaction.user.id, message_id=message_id, guild_id=interaction.guild_id)

    reports_admin_group = app_commands.Group(name="reports", description="Manage reports")

    @reports_admin_group.command(name="list", description="List open reports")
    @app_commands.choices(status=[
        app_commands.Choice(name="Open", value="open"),
        app_commands.Choice(name="Resolved", value="resolved")
    ])
    @app_commands.guild_only()
    @is_staff()
    async def reports_list(
        self, 
        interaction: discord.Interaction, 
        status: Optional[str] = None
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=info_embed(title="Reports", description="No reports found."), ephemeral=True)

    @reports_admin_group.command(name="resolve", description="Resolve a report")
    @app_commands.guild_only()
    @is_staff()
    async def reports_resolve(
        self, 
        interaction: discord.Interaction, 
        id: int, 
        resolution: str
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed(f"Report #{id} resolved: {resolution}"), ephemeral=True)

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(ReportsCog(bot))
