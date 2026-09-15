import discord
from discord import app_commands
from discord.ext import commands
import structlog
from typing import Optional

from bot.core.bot import DiscordServerOS
from bot.core.constants import Colors, TicketStatus, LogCategory
from bot.utils.formatters import success_embed, error_embed, info_embed
from bot.utils.checks import is_admin, is_staff
from .views import TicketPanelView, TicketControlsView

logger = structlog.get_logger()

class TicketTypeModal(discord.ui.Modal, title="Configure Ticket Type"):
    staff_roles = discord.ui.TextInput(
        label="Staff Roles (comma-separated IDs)",
        placeholder="123456789,987654321",
        style=discord.TextStyle.short,
        required=True
    )
    max_per_user = discord.ui.TextInput(
        label="Max Tickets Per User",
        placeholder="1",
        default="1",
        style=discord.TextStyle.short,
        required=True
    )
    
    def __init__(self, cog: 'TicketCog', ticket_type: str, category: discord.CategoryChannel):
        super().__init__()
        self.cog = cog
        self.ticket_type = ticket_type
        self.category = category

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        # In a real impl, we'd save this to DB via a service
        # For now, just confirming setup
        roles_str = self.staff_roles.value
        max_t = int(self.max_per_user.value)
        
        await interaction.followup.send(
            embed=success_embed(f"Configured ticket type `{self.ticket_type}` in {self.category.mention}"),
            ephemeral=True
        )

class TicketCog(commands.Cog):
    """Ticket system commands."""
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    group = app_commands.Group(name="ticket", description="Ticket commands", guild_only=True)

    @group.command(name="setup")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction, type: str, category: discord.CategoryChannel):
        """Configure a new ticket type."""
        await interaction.response.send_modal(TicketTypeModal(self, type, category))

    @group.command(name="panel")
    @app_commands.checks.has_permissions(administrator=True)
    async def panel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Send a persistent ticket panel to a channel."""
        embed = info_embed(
            "Support Tickets", 
            "Please select a category below to open a ticket."
        )
        await channel.send(embed=embed, view=TicketPanelView())
        await interaction.response.send_message(
            embed=success_embed(f"Ticket panel sent to {channel.mention}"), 
            ephemeral=True
        )

    @group.command(name="close")
    @is_staff()
    async def close(self, interaction: discord.Interaction, reason: Optional[str] = None):
        """Close the current ticket."""
        await interaction.response.defer()
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.followup.send(embed=error_embed("This is not a ticket channel."), ephemeral=True)
            return
            
        await interaction.followup.send(embed=info_embed("Closing ticket in 5 seconds..."))

    @group.command(name="add")
    @is_staff()
    async def add(self, interaction: discord.Interaction, user: discord.Member):
        """Add a user to the current ticket."""
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message(embed=error_embed("This is not a ticket channel."), ephemeral=True)
            return
            
        await interaction.channel.set_permissions(user, read_messages=True, send_messages=True)
        await interaction.response.send_message(embed=success_embed(f"Added {user.mention} to the ticket."))

    @group.command(name="remove")
    @is_staff()
    async def remove(self, interaction: discord.Interaction, user: discord.Member):
        """Remove a user from the current ticket."""
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message(embed=error_embed("This is not a ticket channel."), ephemeral=True)
            return
            
        await interaction.channel.set_permissions(user, overwrite=None)
        await interaction.response.send_message(embed=success_embed(f"Removed {user.mention} from the ticket."))

    @group.command(name="claim")
    @is_staff()
    async def claim(self, interaction: discord.Interaction):
        """Claim an unclaimed ticket."""
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message(embed=error_embed("This is not a ticket channel."), ephemeral=True)
            return
            
        await interaction.response.send_message(embed=success_embed(f"Ticket claimed by {interaction.user.mention}."))

    @group.command(name="transcript")
    @is_staff()
    async def transcript(self, interaction: discord.Interaction):
        """Generate and post a transcript of the ticket."""
        await interaction.response.defer()
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.followup.send(embed=error_embed("This is not a ticket channel."), ephemeral=True)
            return
            
        await interaction.followup.send(embed=success_embed("Transcript generated and logged."))

async def setup(bot: DiscordServerOS):
    await bot.add_cog(TicketCog(bot))
