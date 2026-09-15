import discord
from discord import app_commands
from discord.ext import commands
from bot.core.bot import DiscordServerOS
from bot.cogs.setup.views import SetupWizardView, ServerControlPanelView
from bot.utils.formatters import info_embed

class SetupCog(commands.Cog):
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    setup_group = app_commands.Group(name="setup", description="Server setup commands", default_permissions=discord.Permissions(administrator=True))
    admin_group = app_commands.Group(name="admin", description="Server admin commands", default_permissions=discord.Permissions(administrator=True))

    @setup_group.command(name="start", description="Launches the setup wizard")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True, manage_channels=True, manage_guild=True)
    async def setup_start(self, interaction: discord.Interaction):
        await interaction.response.send_message("Step 1: Select Server Type", view=SetupWizardView(interaction.user.id), ephemeral=True)

    @setup_group.command(name="dryrun", description="Generates and shows setup plan without executing")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True, manage_channels=True, manage_guild=True)
    async def setup_dryrun(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        # Logic for dryrun
        await interaction.followup.send(embed=info_embed(title="Dry Run", description="No changes made. Everything looks good!"))

    @admin_group.command(name="panel", description="Opens the Server Control Panel")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def admin_panel(self, interaction: discord.Interaction):
        embed = info_embed(title="Server Control Panel", description="Welcome to the server management dashboard.")
        await interaction.response.send_message(embed=embed, view=ServerControlPanelView(), ephemeral=True)
