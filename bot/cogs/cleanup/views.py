import discord
from discord.ui import View, Button
import structlog
from typing import Optional, Callable
from bot.core.bot import DiscordServerOS
from bot.utils.formatters import success_embed, error_embed

log = structlog.get_logger()

class PurgeConfirmView(View):
    def __init__(self, bot: DiscordServerOS, channel: discord.TextChannel, count: int, check: Optional[Callable] = None):
        super().__init__(timeout=60)
        self.bot = bot
        self.channel = channel
        self.count = count
        self.check = check

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, emoji="✅")
    async def confirm_btn(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        try:
            deleted = await self.channel.purge(limit=self.count, check=self.check)
            await interaction.followup.send(embed=success_embed(f"Deleted {len(deleted)} messages."), ephemeral=True)
            log.info("channel_purged_bulk", channel_id=self.channel.id, count=len(deleted), user_id=interaction.user.id)
        except discord.Forbidden:
            await interaction.followup.send(embed=error_embed("Missing permissions to delete messages."), ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_btn(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=error_embed("Purge cancelled."), ephemeral=True)
