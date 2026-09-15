import discord

class HealthScoreView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔧 Fix Issues", style=discord.ButtonStyle.success)
    async def fix_issues(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Fixing issues...", ephemeral=True)

    @discord.ui.button(label="📋 Full Report", style=discord.ButtonStyle.primary)
    async def full_report(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Generating full report...", ephemeral=True)

    @discord.ui.button(label="🔄 Re-scan", style=discord.ButtonStyle.secondary)
    async def rescan(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Re-scanning...", ephemeral=True)

class DiffView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Repair All", style=discord.ButtonStyle.success)
    async def repair_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Repairing all drift...", ephemeral=True)

    @discord.ui.button(label="Review Changes", style=discord.ButtonStyle.primary)
    async def review(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Reviewing changes...", ephemeral=True)

    @discord.ui.button(label="Dismiss", style=discord.ButtonStyle.secondary)
    async def dismiss(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=None)

class LockdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.locked = False

    @discord.ui.button(label="🚨 Confirm Lockdown", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.locked = True
        button.disabled = True
        await interaction.response.edit_message(content="Lockdown initiated.", view=self)

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.locked:
            await interaction.response.edit_message(content="Lockdown cancelled.", view=None)
