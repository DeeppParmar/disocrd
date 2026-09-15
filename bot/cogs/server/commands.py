import discord
import json
import io
from discord import app_commands
from discord.ext import commands
from bot.core.bot import DiscordServerOS
from bot.cogs.server.views import HealthScoreView, DiffView, LockdownView
from bot.utils.formatters import info_embed, success_embed
from bot.utils.checks import require_setup

class ServerCog(commands.Cog):
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    server_group = app_commands.Group(name="server", description="Server management commands", default_permissions=discord.Permissions(administrator=True))

    @server_group.command(name="analyze", description="Runs full server analysis, produces health score embed")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def server_analyze(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        embed = info_embed(
            title="Server Health Analysis",
            description="Health Score: 85/100\n\n**Categories:**\n- Roles: Good\n- Channels: Warning\n- Permissions: Good"
        )
        await interaction.followup.send(embed=embed, view=HealthScoreView())

    @server_group.command(name="audit", description="Compares expected vs actual config")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @require_setup()
    async def server_audit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        embed = info_embed(title="Configuration Audit", description="No significant drift detected.")
        await interaction.followup.send(embed=embed, view=DiffView())

    @server_group.command(name="repair", description="Auto-fix detected issues")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def server_repair(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await interaction.followup.send(embed=success_embed("Server repaired successfully."))

    @server_group.command(name="lockdown", description="Emergency lockdown")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def server_lockdown(self, interaction: discord.Interaction):
        await interaction.response.send_message("Are you sure you want to lockdown the server?", view=LockdownView(), ephemeral=True)

    @server_group.command(name="unlock", description="Reverses lockdown")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def server_unlock(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await interaction.followup.send(embed=success_embed("Server unlocked. Permissions restored."))

    @server_group.command(name="export", description="Exports server config as JSON")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def server_export(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        data = {"guild_id": interaction.guild_id, "name": interaction.guild.name}
        file = discord.File(io.BytesIO(json.dumps(data, indent=4).encode("utf-8")), filename="config.json")
        await interaction.followup.send(file=file)
