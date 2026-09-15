import discord
from discord.ui import View, Button, Modal, TextInput
import structlog
from bot.core.bot import DiscordServerOS
from bot.utils.formatters import success_embed, info_embed

log = structlog.get_logger()

class ApplicationModal(Modal):
    def __init__(self, bot: DiscordServerOS, app_type: str, fields: list[dict]):
        super().__init__(title=f"{app_type.capitalize()} Application")
        self.bot = bot
        self.app_type = app_type
        
        for i, field in enumerate(fields[:5]):  # Max 5 fields in Discord
            item = TextInput(
                label=field["label"][:45],
                style=field.get("style", discord.TextStyle.short),
                required=field.get("required", True),
                custom_id=f"app_field_{i}"
            )
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        
        # Save to DB and send to configured channel
        answers = {item.custom_id: item.value for item in self.children}
        
        await interaction.followup.send(embed=success_embed("Application submitted successfully!"), ephemeral=True)
        log.info("application_submitted", user_id=interaction.user.id, type=self.app_type)

class ApplicationReviewView(View):
    def __init__(self, bot: DiscordServerOS, app_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.app_id = app_id

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, emoji="✅", custom_id="app:approve")
    async def approve_btn(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed(f"Approved application #{self.app_id}."), ephemeral=True)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger, emoji="❌", custom_id="app:reject")
    async def reject_btn(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed(f"Rejected application #{self.app_id}."), ephemeral=True)

    @discord.ui.button(label="Request Info", style=discord.ButtonStyle.secondary, emoji="❓", custom_id="app:request_info")
    async def request_info_btn(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=info_embed("Info Requested", f"Requested info for application #{self.app_id}."), ephemeral=True)
