import discord
from discord.ui import View, Button
import structlog
from bot.core.bot import DiscordServerOS
from bot.utils.formatters import info_embed

log = structlog.get_logger()

class AnalyticsDashboardView(View):
    def __init__(self, bot: DiscordServerOS, guild_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_id = guild_id

    @discord.ui.button(label="Members", style=discord.ButtonStyle.primary, emoji="📊")
    async def btn_members(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=info_embed("Member Stats", "Stats for members"), ephemeral=True)

    @discord.ui.button(label="Activity", style=discord.ButtonStyle.secondary, emoji="💬")
    async def btn_activity(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=info_embed("Activity Stats", "Stats for activity"), ephemeral=True)

    @discord.ui.button(label="Tickets", style=discord.ButtonStyle.secondary, emoji="🎫")
    async def btn_tickets(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=info_embed("Ticket Stats", "Stats for tickets"), ephemeral=True)

    @discord.ui.button(label="Moderation", style=discord.ButtonStyle.secondary, emoji="🛡️")
    async def btn_moderation(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=info_embed("Moderation Stats", "Stats for moderation"), ephemeral=True)
