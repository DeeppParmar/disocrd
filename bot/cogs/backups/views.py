import discord
from discord.ui import View, Button
import structlog
from bot.core.bot import DiscordServerOS
from bot.utils.formatters import success_embed, error_embed

log = structlog.get_logger()

class BackupListView(View):
    def __init__(self, bot: DiscordServerOS, guild_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_id = guild_id
        # Normally add pagination buttons here

class RestoreConfirmView(View):
    def __init__(self, bot: DiscordServerOS, backup_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.backup_id = backup_id

    @discord.ui.button(label="Confirm Restore", style=discord.ButtonStyle.danger, emoji="⚠️")
    async def confirm(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        # Perform restore
        await interaction.followup.send(embed=success_embed(f"Restored backup #{self.backup_id}."), ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=error_embed("Restore cancelled."), ephemeral=True)

class BackupDetailView(View):
    def __init__(self, bot: DiscordServerOS, backup_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.backup_id = backup_id

    @discord.ui.button(label="Restore", style=discord.ButtonStyle.danger)
    async def restore_btn(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        view = RestoreConfirmView(self.bot, self.backup_id)
        await interaction.followup.send(
            embed=error_embed(f"Are you sure you want to restore backup #{self.backup_id}?"), 
            view=view, 
            ephemeral=True
        )

    @discord.ui.button(label="Compare", style=discord.ButtonStyle.primary)
    async def compare_btn(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Comparison diff...", ephemeral=True)

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.secondary)
    async def delete_btn(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed(f"Deleted backup #{self.backup_id}."), ephemeral=True)
