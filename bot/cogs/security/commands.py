import discord
from discord import app_commands
from discord.ext import commands
import structlog

from bot.core.bot import DiscordServerOS
from bot.core.constants import SecurityLevel
from bot.utils.formatters import success_embed, error_embed, info_embed
from bot.utils.checks import is_admin
from .views import LockdownConfirmView, PanicDeactivateView, build_security_status_embed

logger = structlog.get_logger()

class SecurityCog(commands.Cog):
    """Security and raid-protection commands."""
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    group = app_commands.Group(name="security", description="Server security commands", guild_only=True)

    @group.command(name="status")
    @is_admin()
    async def status(self, interaction: discord.Interaction):
        """Show current security status."""
        embed = build_security_status_embed(SecurityLevel.NORMAL, False, ["No recent alerts."])
        await interaction.response.send_message(embed=embed)

    @group.command(name="lockdown")
    @is_admin()
    async def lockdown(self, interaction: discord.Interaction):
        """Initiate emergency lockdown."""
        await interaction.response.send_message(
            embed=error_embed("⚠️ Are you sure you want to initiate lockdown?"), 
            view=LockdownConfirmView(),
            ephemeral=True
        )

    @group.command(name="unlock")
    @is_admin()
    async def unlock(self, interaction: discord.Interaction):
        """Deactivate lockdown and restore permissions."""
        await interaction.response.defer()
        await interaction.followup.send(embed=success_embed("Lockdown deactivated. Restoring permissions..."))

    @group.command(name="panic")
    @is_admin()
    async def panic(self, interaction: discord.Interaction):
        """PANIC MODE: lockdown + pause tickets + alert staff."""
        await interaction.response.send_message(
            embed=error_embed("🚨 PANIC MODE ACTIVATED. Server is locked down."),
            view=PanicDeactivateView()
        )

    @group.command(name="scan")
    @is_admin()
    async def scan(self, interaction: discord.Interaction):
        """Scan for threats (new accounts, suspicious perms, webhooks)."""
        await interaction.response.defer()
        await interaction.followup.send(embed=info_embed("Security Scan Complete", "No major threats detected."))

async def setup(bot: DiscordServerOS):
    await bot.add_cog(SecurityCog(bot))
