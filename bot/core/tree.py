"""Custom CommandTree implementation."""

import discord
from discord.app_commands import AppCommandError
from discord.ext import commands
import structlog

logger = structlog.get_logger(__name__)


class BotCommandTree(discord.app_commands.CommandTree):
    """Custom command tree with specialized error handling."""
    
    async def on_error(
        self,
        interaction: discord.Interaction,
        error: AppCommandError
    ) -> None:
        """Global error handler for application commands.
        
        Args:
            interaction: The interaction that triggered the error.
            error: The error that occurred.
        """
        if interaction.is_expired():
            return
            
        message = "An unexpected error occurred while processing your command."
        
        if isinstance(error, discord.app_commands.MissingPermissions):
            missing_perms = ", ".join(error.missing_permissions)
            message = f"You are missing the following permissions to run this command: `{missing_perms}`"
        
        elif isinstance(error, discord.app_commands.BotMissingPermissions):
            missing_perms = ", ".join(error.missing_permissions)
            message = f"I am missing the following permissions to execute this command: `{missing_perms}`"
            
        elif isinstance(error, discord.app_commands.CommandOnCooldown):
            message = f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds."
            
        elif isinstance(error, discord.app_commands.CheckFailure):
            message = "You do not meet the requirements to run this command."
            
        elif isinstance(error, discord.app_commands.TransformerError):
            message = f"Could not process one of the arguments provided: {error.value}"
            
        else:
            logger.exception(
                "Unhandled application command error",
                error=error,
                command=interaction.command.name if interaction.command else "Unknown",
                user_id=interaction.user.id,
                guild_id=interaction.guild_id
            )
            
        if not interaction.response.is_done():
            await interaction.response.send_message(message, ephemeral=True)
        else:
            await interaction.followup.send(message, ephemeral=True)
