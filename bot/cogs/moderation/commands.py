from __future__ import annotations

import re
from datetime import timedelta
import structlog

import discord
from discord import app_commands
from discord.ext import commands

from bot.core.bot import DiscordServerOS
from bot.core.constants import ModerationAction
from bot.utils.formatters import success_embed, error_embed, warning_embed, info_embed, PaginatorView, format_duration, format_timestamp
from bot.utils.checks import is_moderator
from .views import CaseEmbed, WarningListView, CaseDetailView

logger = structlog.get_logger(__name__)

def parse_duration(duration_str: str) -> timedelta | None:
    """Parse a duration string into a timedelta."""
    if not duration_str:
        return None
        
    pattern = re.compile(r"^(?:(?P<days>\d+)d)?(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?(?:(?P<seconds>\d+)s)?$")
    match = pattern.match(duration_str)
    
    if not match:
        return None
        
    kwargs = {k: int(v) for k, v in match.groupdict().items() if v is not None}
    if not kwargs:
        return None
        
    return timedelta(**kwargs)


@app_commands.guild_only()
@app_commands.default_permissions(moderate_members=True)
class ModerationCog(commands.GroupCog, name="mod"):
    """Moderation commands for managing users."""
    
    def __init__(self, bot: DiscordServerOS) -> None:
        self.bot = bot
        # self.service = ModerationService(bot) # Assumed to exist or will be accessed via self.bot.services

    async def _check_hierarchy(self, interaction: discord.Interaction, target: discord.Member) -> bool:
        """Check if the user can moderate the target based on role hierarchy."""
        if isinstance(interaction.user, discord.Member):
            if interaction.user.top_role <= target.top_role:
                await interaction.followup.send(
                    embed=error_embed("You cannot moderate a member with an equal or higher role."),
                    ephemeral=True
                )
                return False
        if interaction.guild and interaction.guild.me.top_role <= target.top_role:
            await interaction.followup.send(
                embed=error_embed("I cannot moderate a member with an equal or higher role than my highest role."),
                ephemeral=True
            )
            return False
        return True

    @app_commands.command(name="warn", description="Warn a user.")
    @app_commands.describe(user="The user to warn", reason="The reason for the warning")
    async def warn_command(self, interaction: discord.Interaction, user: discord.Member, reason: str) -> None:
        """Warn a member."""
        await interaction.response.defer(ephemeral=True)
        
        if not await self._check_hierarchy(interaction, user):
            return

        # Implementation logic to create warning via ModerationService
        # Case logic would go here
        
        try:
            await user.send(embed=warning_embed(f"You have been warned in {interaction.guild.name}\nReason: {reason}"))
        except discord.Forbidden:
            pass

        await interaction.followup.send(
            embed=success_embed(f"Successfully warned {user.mention}."),
            ephemeral=True
        )

    @app_commands.command(name="timeout", description="Timeout a user.")
    @app_commands.describe(
        user="The user to timeout", 
        duration="Duration (e.g. 1h, 30m, 1d)", 
        reason="The reason for the timeout"
    )
    async def timeout_command(
        self, 
        interaction: discord.Interaction, 
        user: discord.Member, 
        duration: str, 
        reason: str
    ) -> None:
        """Timeout a member."""
        await interaction.response.defer(ephemeral=True)
        
        if not await self._check_hierarchy(interaction, user):
            return
            
        td = parse_duration(duration)
        if td is None:
            await interaction.followup.send(
                embed=error_embed("Invalid duration format. Use e.g. 1h, 30m, 1d"),
                ephemeral=True
            )
            return
            
        if td > timedelta(days=28):
            await interaction.followup.send(
                embed=error_embed("Timeout duration cannot exceed 28 days."),
                ephemeral=True
            )
            return

        try:
            await user.send(embed=warning_embed(f"You have been timed out in {interaction.guild.name} for {duration}\nReason: {reason}"))
        except discord.Forbidden:
            pass

        try:
            await user.timeout(discord.utils.utcnow() + td, reason=f"{interaction.user}: {reason}")
            await interaction.followup.send(
                embed=success_embed(f"Successfully timed out {user.mention} for {duration}."),
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                embed=error_embed("I lack permissions to timeout this user."),
                ephemeral=True
            )

    @app_commands.command(name="kick", description="Kick a user from the server.")
    @app_commands.describe(user="The user to kick", reason="The reason for the kick")
    async def kick_command(self, interaction: discord.Interaction, user: discord.Member, reason: str) -> None:
        """Kick a member."""
        await interaction.response.defer(ephemeral=True)
        
        if not await self._check_hierarchy(interaction, user):
            return
            
        try:
            await user.send(embed=warning_embed(f"You have been kicked from {interaction.guild.name}\nReason: {reason}"))
        except discord.Forbidden:
            pass

        try:
            await user.kick(reason=f"{interaction.user}: {reason}")
            await interaction.followup.send(
                embed=success_embed(f"Successfully kicked {user.mention}."),
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                embed=error_embed("I lack permissions to kick this user."),
                ephemeral=True
            )

    @app_commands.command(name="ban", description="Ban a user from the server.")
    @app_commands.describe(
        user="The user to ban", 
        reason="The reason for the ban",
        delete_days="Days of messages to delete (0-7)"
    )
    async def ban_command(
        self, 
        interaction: discord.Interaction, 
        user: discord.Member, 
        reason: str, 
        delete_days: int = 0
    ) -> None:
        """Ban a member."""
        await interaction.response.defer(ephemeral=True)
        
        if not await self._check_hierarchy(interaction, user):
            return
            
        if not 0 <= delete_days <= 7:
            await interaction.followup.send(
                embed=error_embed("Delete days must be between 0 and 7."),
                ephemeral=True
            )
            return
            
        try:
            await user.send(embed=error_embed(f"You have been banned from {interaction.guild.name}\nReason: {reason}"))
        except discord.Forbidden:
            pass

        try:
            await user.ban(reason=f"{interaction.user}: {reason}", delete_message_days=delete_days)
            await interaction.followup.send(
                embed=success_embed(f"Successfully banned {user.mention}."),
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                embed=error_embed("I lack permissions to ban this user."),
                ephemeral=True
            )

    @app_commands.command(name="unban", description="Unban a user.")
    @app_commands.describe(user="The user to unban", reason="The reason for the unban")
    async def unban_command(self, interaction: discord.Interaction, user: discord.User, reason: str) -> None:
        """Unban a user."""
        await interaction.response.defer(ephemeral=True)
        
        try:
            await interaction.guild.unban(user, reason=f"{interaction.user}: {reason}")
            await interaction.followup.send(
                embed=success_embed(f"Successfully unbanned {user.mention}."),
                ephemeral=True
            )
        except discord.NotFound:
            await interaction.followup.send(
                embed=error_embed("User is not banned."),
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                embed=error_embed("I lack permissions to unban users."),
                ephemeral=True
            )

    @app_commands.command(name="softban", description="Softban a user (ban and immediate unban to clear messages).")
    @app_commands.describe(user="The user to softban", reason="The reason for the softban")
    async def softban_command(self, interaction: discord.Interaction, user: discord.Member, reason: str) -> None:
        """Softban a member."""
        await interaction.response.defer(ephemeral=True)
        
        if not await self._check_hierarchy(interaction, user):
            return
            
        try:
            await user.ban(reason=f"Softban by {interaction.user}: {reason}", delete_message_days=7)
            await interaction.guild.unban(user, reason="Softban unban")
            await interaction.followup.send(
                embed=success_embed(f"Successfully softbanned {user.mention}."),
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                embed=error_embed("I lack permissions to ban/unban this user."),
                ephemeral=True
            )

    @app_commands.command(name="warnings", description="Show a user's warnings.")
    @app_commands.describe(user="The user to view warnings for")
    async def warnings_command(self, interaction: discord.Interaction, user: discord.Member) -> None:
        """Show warnings for a member."""
        await interaction.response.defer(ephemeral=True)
        
        # Placeholder for DB fetch logic
        embed = info_embed(f"Warnings for {user.display_name}")
        embed.description = "No warnings found."
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="modhistory", description="Show full moderation history for a user.")
    @app_commands.describe(user="The user to view history for")
    async def modhistory_command(self, interaction: discord.Interaction, user: discord.Member) -> None:
        """Show full moderation history."""
        await interaction.response.defer(ephemeral=True)
        
        embed = info_embed(f"Moderation History for {user.display_name}")
        embed.description = "No history found."
        
        await interaction.followup.send(embed=embed, ephemeral=True)
