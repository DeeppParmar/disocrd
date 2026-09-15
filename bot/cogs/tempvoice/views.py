import discord
from discord.ui import View, Button, Modal, TextInput
import structlog
from bot.core.bot import DiscordServerOS
from bot.utils.formatters import success_embed, error_embed

log = structlog.get_logger()

class RenameModal(Modal, title="Rename Channel"):
    name_input = TextInput(
        label="New Channel Name",
        style=discord.TextStyle.short,
        placeholder="e.g. Chill Lounge",
        required=True,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        if interaction.user.voice and interaction.user.voice.channel:
            await interaction.user.voice.channel.edit(name=self.name_input.value)
            await interaction.followup.send(embed=success_embed(f"Renamed to {self.name_input.value}"), ephemeral=True)
        else:
            await interaction.followup.send(embed=error_embed("You are not in a voice channel."), ephemeral=True)

class LimitModal(Modal, title="Set User Limit"):
    limit_input = TextInput(
        label="User Limit (0-99)",
        style=discord.TextStyle.short,
        placeholder="0 for unlimited",
        required=True,
        max_length=2
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        try:
            limit = int(self.limit_input.value)
            if limit < 0 or limit > 99:
                raise ValueError
        except ValueError:
            return await interaction.followup.send(embed=error_embed("Please enter a valid number between 0 and 99."), ephemeral=True)
            
        if interaction.user.voice and interaction.user.voice.channel:
            await interaction.user.voice.channel.edit(user_limit=limit)
            await interaction.followup.send(embed=success_embed(f"Limit set to {limit}"), ephemeral=True)
        else:
            await interaction.followup.send(embed=error_embed("You are not in a voice channel."), ephemeral=True)

class TempVoiceControlView(View):
    def __init__(self, bot: DiscordServerOS):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Lock", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="tempvoice:lock")
    async def lock_btn(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        if interaction.user.voice and interaction.user.voice.channel:
            await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, connect=False)
            await interaction.followup.send(embed=success_embed("Locked."), ephemeral=True)
        else:
            await interaction.followup.send(embed=error_embed("Not in a voice channel."), ephemeral=True)

    @discord.ui.button(label="Unlock", style=discord.ButtonStyle.green, emoji="🔓", custom_id="tempvoice:unlock")
    async def unlock_btn(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        if interaction.user.voice and interaction.user.voice.channel:
            await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, connect=True)
            await interaction.followup.send(embed=success_embed("Unlocked."), ephemeral=True)

    @discord.ui.button(label="Rename", style=discord.ButtonStyle.primary, emoji="📝", custom_id="tempvoice:rename")
    async def rename_btn(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.send_modal(RenameModal())

    @discord.ui.button(label="Limit", style=discord.ButtonStyle.secondary, emoji="👥", custom_id="tempvoice:limit")
    async def limit_btn(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.send_modal(LimitModal())

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="tempvoice:delete")
    async def delete_btn(self, interaction: discord.Interaction, button: Button) -> None:
        await interaction.response.defer(ephemeral=True)
        if interaction.user.voice and interaction.user.voice.channel:
            await interaction.user.voice.channel.delete(reason="User requested deletion")
            await interaction.followup.send(embed=success_embed("Deleted."), ephemeral=True)
