import discord
from bot.utils.formatters import success_embed, error_embed

class TicketRatingModal(discord.ui.Modal, title="Rate Your Support Experience"):
    rating = discord.ui.TextInput(
        label="Rating (1-5)",
        placeholder="5",
        min_length=1,
        max_length=1,
        style=discord.TextStyle.short,
        required=True
    )
    feedback = discord.ui.TextInput(
        label="Feedback (Optional)",
        style=discord.TextStyle.paragraph,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            r = int(self.rating.value)
            if r < 1 or r > 5:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(embed=error_embed("Rating must be a number between 1 and 5."), ephemeral=True)
            return
        
        await interaction.response.send_message(embed=success_embed("Thank you for your feedback!"), ephemeral=True)


class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        options = [
            discord.SelectOption(label="General Support", description="General questions or issues", emoji="❓"),
            discord.SelectOption(label="Billing", description="Payment or subscription issues", emoji="💳"),
            discord.SelectOption(label="Report", description="Report a user or bug", emoji="⚠️")
        ]
        
        self.select = discord.ui.Select(
            custom_id="ticket_panel:select",
            placeholder="Select a ticket type...",
            options=options,
            min_values=1,
            max_values=1
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=success_embed(f"Creating {self.select.values[0]} ticket..."), ephemeral=True)
        # Create ticket logic would go here

class TicketControlsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, custom_id="ticket:close", emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketRatingModal())

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.primary, custom_id="ticket:claim", emoji="👋")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket claimed.", ephemeral=True)

    @discord.ui.button(label="Add User", style=discord.ButtonStyle.secondary, custom_id="ticket:add", emoji="👥")
    async def add_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Use `/ticket add` command.", ephemeral=True)

    @discord.ui.button(label="Transcript", style=discord.ButtonStyle.secondary, custom_id="ticket:transcript", emoji="📝")
    async def get_transcript(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Generating transcript...", ephemeral=True)
