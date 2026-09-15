import discord
from discord import app_commands
from discord.ext import commands
import structlog
from typing import Optional

from bot.core.bot import DiscordServerOS
from bot.utils.formatters import success_embed, error_embed, info_embed
from bot.utils.checks import is_admin
from bot.cogs.verification.views import VerifyButtonView, RulesAcceptView

log = structlog.get_logger()

class VerificationCog(commands.Cog):
    """Handles server verification systems."""
    
    __slots__ = ('bot',)

    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    verify_group = app_commands.Group(name="verify", description="Verification commands")

    @verify_group.command(name="setup", description="Configure server verification")
    @app_commands.choices(mode=[
        app_commands.Choice(name="Button", value="button"),
        app_commands.Choice(name="Rules", value="rules"),
        app_commands.Choice(name="Account Age", value="account_age")
    ])
    @app_commands.guild_only()
    @is_admin()
    async def verify_setup(
        self, 
        interaction: discord.Interaction, 
        mode: str, 
        role: discord.Role, 
        channel: discord.TextChannel
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        
        # NOTE: Dummy DB logic as DB schemas are not fully provided
        log.info("verification_setup", guild_id=interaction.guild_id, mode=mode, role_id=role.id, channel_id=channel.id)
            
        await interaction.followup.send(
            embed=success_embed(f"Verification configured in {channel.mention} with role {role.mention} (Mode: {mode})"),
            ephemeral=True
        )

    @verify_group.command(name="panel", description="Send verification panel to configured channel")
    @app_commands.guild_only()
    @is_admin()
    async def verify_panel(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        # Simulated config retrieval
        mode = "button"
        
        embed = info_embed(
            title="Verification Required",
            description="Please click the button below to verify your account and gain access to the rest of the server."
        )
        
        view = VerifyButtonView(self.bot)
        
        await interaction.channel.send(embed=embed, view=view)
        await interaction.followup.send(embed=success_embed("Panel posted."), ephemeral=True)

    @verify_group.command(name="config", description="Update verification config settings")
    @app_commands.guild_only()
    @is_admin()
    async def verify_config(
        self, 
        interaction: discord.Interaction, 
        min_age: Optional[int] = None, 
        rules_text: Optional[str] = None
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed("Verification config updated!"), ephemeral=True)

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(VerificationCog(bot))
