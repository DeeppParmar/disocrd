import discord
from discord.ui import View, Button
import structlog
from bot.core.bot import DiscordServerOS
from bot.utils.formatters import success_embed

log = structlog.get_logger()

class SuggestionVoteView(View):
    def __init__(self, bot: DiscordServerOS, suggestion_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.suggestion_id = suggestion_id
        
        # Dynamically set custom_ids for persistence
        self.upvote_btn = Button(style=discord.ButtonStyle.secondary, label="👍 (0)", custom_id=f"suggestion:up:{suggestion_id}")
        self.upvote_btn.callback = self.upvote
        
        self.downvote_btn = Button(style=discord.ButtonStyle.secondary, label="👎 (0)", custom_id=f"suggestion:down:{suggestion_id}")
        self.downvote_btn.callback = self.downvote
        
        self.add_item(self.upvote_btn)
        self.add_item(self.downvote_btn)

    async def upvote(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed("You upvoted this suggestion!"), ephemeral=True)

    async def downvote(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed("You downvoted this suggestion!"), ephemeral=True)

class SuggestionManageView(View):
    def __init__(self, bot: DiscordServerOS, suggestion_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.suggestion_id = suggestion_id

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, emoji="✅", custom_id="manage_sug:approve")
    async def approve(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed("Approved suggestion."), ephemeral=True)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger, emoji="❌", custom_id="manage_sug:reject")
    async def reject(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed("Rejected suggestion."), ephemeral=True)

    @discord.ui.button(label="Implemented", style=discord.ButtonStyle.primary, emoji="⭐", custom_id="manage_sug:implemented")
    async def implemented(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed("Marked suggestion as implemented."), ephemeral=True)

    @discord.ui.button(label="Duplicate", style=discord.ButtonStyle.secondary, emoji="📋", custom_id="manage_sug:duplicate")
    async def duplicate(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed("Marked suggestion as duplicate."), ephemeral=True)
