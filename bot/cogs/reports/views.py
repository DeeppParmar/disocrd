import discord
from discord.ui import View, Button, Modal, TextInput
import structlog
from bot.core.bot import DiscordServerOS
from bot.utils.formatters import success_embed

log = structlog.get_logger()

class ReportActionView(View):
    def __init__(self, bot: DiscordServerOS, report_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.report_id = report_id

    @discord.ui.button(label="Investigate", style=discord.ButtonStyle.primary, emoji="🔍", custom_id="report:investigate")
    async def investigate(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed("Marked as under investigation."), ephemeral=True)

    @discord.ui.button(label="Resolve", style=discord.ButtonStyle.green, emoji="✅", custom_id="report:resolve")
    async def resolve(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed("Report resolved."), ephemeral=True)

    @discord.ui.button(label="Dismiss", style=discord.ButtonStyle.secondary, emoji="❌", custom_id="report:dismiss")
    async def dismiss(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed("Report dismissed."), ephemeral=True)

class ReportModal(Modal, title="Detailed Report"):
    reason = TextInput(
        label="Reason for report",
        style=discord.TextStyle.short,
        placeholder="Why are you reporting this?",
        required=True,
        max_length=100
    )
    
    evidence = TextInput(
        label="Evidence/Details",
        style=discord.TextStyle.paragraph,
        placeholder="Provide context, links to messages, etc.",
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed("Detailed report submitted successfully."), ephemeral=True)
