import discord
from discord.ui import View, Button
from datetime import datetime, timezone
import structlog
from bot.utils.formatters import success_embed, error_embed
from bot.core.bot import DiscordServerOS

log = structlog.get_logger()

class VerifyButtonView(View):
    def __init__(self, bot: DiscordServerOS, min_age_days: int = None, verified_role_id: int = None, unverified_role_id: int = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.min_age_days = min_age_days
        self.verified_role_id = verified_role_id
        self.unverified_role_id = unverified_role_id

    @discord.ui.button(label="Verify Me", style=discord.ButtonStyle.green, emoji="✅", custom_id="verify:button")
    async def verify_button(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        
        if self.min_age_days:
            age_days = (datetime.now(timezone.utc) - interaction.user.created_at).days
            if age_days < self.min_age_days:
                await interaction.followup.send(
                    embed=error_embed(f"Your account must be at least {self.min_age_days} days old to verify. Currently {age_days} days old."), 
                    ephemeral=True
                )
                return

        guild = interaction.guild
        verified_role = guild.get_role(self.verified_role_id) if self.verified_role_id else None
        unverified_role = guild.get_role(self.unverified_role_id) if self.unverified_role_id else None

        roles_to_add = [verified_role] if verified_role else []
        roles_to_remove = [unverified_role] if unverified_role and unverified_role in interaction.user.roles else []

        try:
            if roles_to_add:
                await interaction.user.add_roles(*roles_to_add, reason="Verification passed")
            if roles_to_remove:
                await interaction.user.remove_roles(*roles_to_remove, reason="Verification passed")
            await interaction.followup.send(embed=success_embed("You have been verified!"), ephemeral=True)
            log.info("user_verified", user_id=interaction.user.id, guild_id=guild.id)
        except discord.Forbidden:
            await interaction.followup.send(embed=error_embed("I don't have permission to manage your roles."), ephemeral=True)

class RulesAcceptView(View):
    def __init__(self, bot: DiscordServerOS, verified_role_id: int = None, unverified_role_id: int = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.verified_role_id = verified_role_id
        self.unverified_role_id = unverified_role_id

    @discord.ui.button(label="I Accept the Rules", style=discord.ButtonStyle.primary, emoji="📜", custom_id="verify:rules")
    async def rules_button(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        verified_role = guild.get_role(self.verified_role_id) if self.verified_role_id else None
        unverified_role = guild.get_role(self.unverified_role_id) if self.unverified_role_id else None

        roles_to_add = [verified_role] if verified_role else []
        roles_to_remove = [unverified_role] if unverified_role and unverified_role in interaction.user.roles else []

        try:
            if roles_to_add:
                await interaction.user.add_roles(*roles_to_add, reason="Rules accepted")
            if roles_to_remove:
                await interaction.user.remove_roles(*roles_to_remove, reason="Rules accepted")
            await interaction.followup.send(embed=success_embed("Thank you for accepting the rules. You are now verified!"), ephemeral=True)
            log.info("rules_accepted", user_id=interaction.user.id, guild_id=guild.id)
        except discord.Forbidden:
            await interaction.followup.send(embed=error_embed("I don't have permission to manage your roles."), ephemeral=True)
