from __future__ import annotations

import discord
from discord import ui
from typing import Any, List

from bot.utils.formatters import info_embed, success_embed

def CaseEmbed(case_data: dict[str, Any]) -> discord.Embed:
    """Build a clean case embed."""
    embed = info_embed(f"Case #{case_data.get('id')} | {case_data.get('action')}")
    embed.add_field(name="User", value=f"<@{case_data.get('user_id')}>", inline=True)
    embed.add_field(name="Moderator", value=f"<@{case_data.get('mod_id')}>", inline=True)
    embed.add_field(name="Reason", value=case_data.get('reason', 'No reason provided'), inline=False)
    
    if case_data.get('notes'):
        notes_str = "\n".join(f"- {note}" for note in case_data['notes'])
        embed.add_field(name="Notes", value=notes_str, inline=False)
        
    return embed

class AddNoteModal(ui.Modal, title="Add Note to Case"):
    note = ui.TextInput(
        label="Note content",
        style=discord.TextStyle.paragraph,
        placeholder="Enter your note here...",
        required=True,
        max_length=1000
    )

    def __init__(self, case_id: int):
        super().__init__()
        self.case_id = case_id

    async def on_submit(self, interaction: discord.Interaction) -> None:
        # Implementation to save note to DB
        await interaction.response.send_message(
            embed=success_embed(f"Note added to Case #{self.case_id}."),
            ephemeral=True
        )

class CaseDetailView(ui.View):
    def __init__(self, case_id: int):
        super().__init__(timeout=180)
        self.case_id = case_id

    @ui.button(label="Add Note", style=discord.ButtonStyle.secondary, custom_id="add_case_note")
    async def add_note_btn(self, interaction: discord.Interaction, button: ui.Button) -> None:
        await interaction.response.send_modal(AddNoteModal(self.case_id))

class WarningListView(ui.View):
    def __init__(self, user_id: int, warnings: List[dict[str, Any]]):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.warnings = warnings
        # Paginator logic would be implemented here
