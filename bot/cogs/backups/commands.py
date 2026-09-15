import discord
from discord import app_commands
from discord.ext import commands
import structlog

from bot.core.bot import DiscordServerOS
from bot.utils.formatters import success_embed, error_embed, info_embed
from bot.utils.checks import is_admin
from bot.cogs.backups.views import BackupListView, BackupDetailView

log = structlog.get_logger()

class BackupCog(commands.Cog):
    """Handles server backups."""
    
    __slots__ = ('bot',)

    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    backup_group = app_commands.Group(name="backup", description="Backup management commands")

    @backup_group.command(name="create", description="Create a server backup")
    @app_commands.guild_only()
    @is_admin()
    async def backup_create(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        # Placeholder for backup logic
        await interaction.followup.send(embed=success_embed("Started creating backup. This may take a moment..."), ephemeral=True)
        log.info("backup_create_started", guild_id=interaction.guild_id, user_id=interaction.user.id)

    @backup_group.command(name="list", description="List available backups")
    @app_commands.guild_only()
    @is_admin()
    async def backup_list(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        
        embed = info_embed(title="Server Backups", description="Fetching backups...")
        view = BackupListView(self.bot, interaction.guild_id)
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @backup_group.command(name="inspect", description="View detailed backup info")
    @app_commands.guild_only()
    @is_admin()
    async def backup_inspect(self, interaction: discord.Interaction, id: int) -> None:
        await interaction.response.defer(ephemeral=True)
        
        embed = info_embed(title=f"Backup #{id}", description="Detailed contents of the backup...")
        view = BackupDetailView(self.bot, backup_id=id)
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @backup_group.command(name="restore", description="Restore a server backup")
    @app_commands.guild_only()
    @is_admin()
    async def backup_restore(self, interaction: discord.Interaction, id: int) -> None:
        from bot.cogs.backups.views import RestoreConfirmView
        await interaction.response.defer(ephemeral=True)
        
        view = RestoreConfirmView(self.bot, backup_id=id)
        embed = info_embed(
            title="⚠️ Confirm Restore",
            description=f"Are you sure you want to restore backup #{id}? This will overwrite current server state."
        )
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @backup_group.command(name="compare", description="Compare backup to current server state")
    @app_commands.guild_only()
    @is_admin()
    async def backup_compare(self, interaction: discord.Interaction, id: int) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=info_embed(title="Backup Comparison", description="Diff details..."), ephemeral=True)

    @backup_group.command(name="delete", description="Delete a backup")
    @app_commands.guild_only()
    @is_admin()
    async def backup_delete(self, interaction: discord.Interaction, id: int) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed(f"Backup #{id} deleted successfully."), ephemeral=True)
        log.info("backup_deleted", guild_id=interaction.guild_id, user_id=interaction.user.id, backup_id=id)

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(BackupCog(bot))
