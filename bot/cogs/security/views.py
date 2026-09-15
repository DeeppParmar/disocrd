import discord
from bot.utils.formatters import success_embed, error_embed
from bot.core.constants import Colors, SecurityLevel

class LockdownConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Confirm Lockdown", style=discord.ButtonStyle.danger, emoji="🚨")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=error_embed("Lockdown initiated!"), ephemeral=False)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Lockdown cancelled.", ephemeral=True)
        self.stop()

class PanicDeactivateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Deactivate Panic Mode", style=discord.ButtonStyle.success, emoji="🔓", custom_id="security:panic_deactivate")
    async def deactivate(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=success_embed("Panic mode deactivated."), ephemeral=False)

def build_security_status_embed(level: SecurityLevel, lockdown: bool, alerts: list[str]) -> discord.Embed:
    embed = discord.Embed(
        title="Security Status",
        color=Colors.SUCCESS if not lockdown else Colors.ERROR
    )
    embed.add_field(name="Threat Level", value=level.name, inline=True)
    embed.add_field(name="Lockdown Status", value="Active" if lockdown else "Inactive", inline=True)
    
    alerts_text = "\n".join(alerts) if alerts else "None"
    embed.add_field(name="Recent Alerts", value=alerts_text, inline=False)
    
    return embed
