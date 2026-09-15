import discord
from discord import app_commands
from discord.ext import commands
import structlog
from typing import Optional

from bot.core.bot import DiscordServerOS
from bot.utils.formatters import success_embed, info_embed
from bot.utils.checks import is_admin
from bot.cogs.automod.views import AutoModDashboardView

log = structlog.get_logger()

class AutoModCog(commands.Cog):
    """Handles automod configurations."""
    
    __slots__ = ('bot',)

    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    automod_group = app_commands.Group(name="automod", description="AutoMod management")

    @automod_group.command(name="dashboard", description="Show AutoMod status")
    @app_commands.guild_only()
    @is_admin()
    async def automod_dashboard(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        
        embed = info_embed(
            title="🛡️ AutoMod Dashboard",
            description="Manage server automod rules."
        )
        
        view = AutoModDashboardView(self.bot, interaction.guild_id)
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @automod_group.command(name="enable", description="Enable an AutoMod rule")
    @app_commands.choices(rule=[
        app_commands.Choice(name="Spam Filter", value="spam"),
        app_commands.Choice(name="Mention Spam", value="mention_spam"),
        app_commands.Choice(name="Invite Links", value="invite_links"),
        app_commands.Choice(name="Profanity Filter", value="profanity")
    ])
    @app_commands.guild_only()
    @is_admin()
    async def automod_enable(self, interaction: discord.Interaction, rule: str) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed(f"Enabled AutoMod rule: `{rule}`"), ephemeral=True)
        log.info("automod_rule_enabled", guild_id=interaction.guild_id, rule=rule)

    @automod_group.command(name="disable", description="Disable an AutoMod rule")
    @app_commands.choices(rule=[
        app_commands.Choice(name="Spam Filter", value="spam"),
        app_commands.Choice(name="Mention Spam", value="mention_spam"),
        app_commands.Choice(name="Invite Links", value="invite_links"),
        app_commands.Choice(name="Profanity Filter", value="profanity")
    ])
    @app_commands.guild_only()
    @is_admin()
    async def automod_disable(self, interaction: discord.Interaction, rule: str) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed(f"Disabled AutoMod rule: `{rule}`"), ephemeral=True)
        log.info("automod_rule_disabled", guild_id=interaction.guild_id, rule=rule)

    @automod_group.command(name="exempt", description="Exempt a role from an AutoMod rule")
    @app_commands.choices(rule=[
        app_commands.Choice(name="Spam Filter", value="spam"),
        app_commands.Choice(name="Mention Spam", value="mention_spam"),
        app_commands.Choice(name="Invite Links", value="invite_links"),
        app_commands.Choice(name="Profanity Filter", value="profanity")
    ])
    @app_commands.guild_only()
    @is_admin()
    async def automod_exempt(self, interaction: discord.Interaction, role: discord.Role, rule: str) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed(f"Exempted {role.mention} from AutoMod rule: `{rule}`"), ephemeral=True)

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(AutoModCog(bot))
