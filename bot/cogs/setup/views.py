import discord
from discord.ext import commands
from bot.core.constants import ServerType, Colors, SetupPhase, SecurityLevel
from bot.utils.formatters import success_embed, error_embed, warning_embed, info_embed

class SetupWizardView(discord.ui.View):
    __slots__ = ('author_id', 'server_type', 'features', 'security_level', 'current_step')

    def __init__(self, author_id: int):
        super().__init__(timeout=300)
        self.author_id = author_id
        self.server_type = None
        self.features = []
        self.security_level = None
        self.current_step = 1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the original author can use this.", ephemeral=True)
            return False
        return True

    @discord.ui.select(
        placeholder="Select Server Type...",
        options=[
            discord.SelectOption(label="Community", value="Community", description="General community server"),
            discord.SelectOption(label="Gaming", value="Gaming", description="Gaming and esports"),
            discord.SelectOption(label="Creator", value="Creator", description="Content creators and streamers"),
            discord.SelectOption(label="Support", value="Support", description="Customer or product support"),
            discord.SelectOption(label="Study", value="Study", description="Study groups and education"),
            discord.SelectOption(label="Business", value="Business", description="Business and companies"),
            discord.SelectOption(label="Friends", value="Friends", description="Private friend groups"),
            discord.SelectOption(label="Custom", value="Custom", description="Custom setup"),
        ]
    )
    async def select_server_type(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.server_type = select.values[0]
        self.current_step = 2
        await self.update_view(interaction)

    async def update_view(self, interaction: discord.Interaction):
        # Update UI based on step
        self.clear_items()
        
        if self.current_step == 2:
            select = discord.ui.Select(
                placeholder="Select Features...",
                min_values=1, max_values=10,
                options=[
                    discord.SelectOption(label=f, value=f) for f in 
                    ["Roles", "Channels", "Tickets", "Moderation", "Verification", "AutoMod", "Logging", "Welcome", "Security", "Backup"]
                ]
            )
            select.callback = self.select_features
            self.add_item(select)
            await interaction.response.edit_message(content="Step 2: Select Features", view=self)

        elif self.current_step == 3:
            select = discord.ui.Select(
                placeholder="Select Security Level...",
                options=[
                    discord.SelectOption(label=level, value=level) for level in ["Basic", "Balanced", "Strict", "Maximum"]
                ]
            )
            select.callback = self.select_security
            self.add_item(select)
            await interaction.response.edit_message(content="Step 3: Select Security Level", view=self)
            
        elif self.current_step == 4:
            # Preview step
            embed = info_embed(
                title="Setup Preview",
                description=f"**Type:** {self.server_type}\n**Features:** {', '.join(self.features)}\n**Security:** {self.security_level}"
            )
            build_btn = discord.ui.Button(label="Build", style=discord.ButtonStyle.success)
            dryrun_btn = discord.ui.Button(label="Dry Run", style=discord.ButtonStyle.secondary)
            cancel_btn = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger)
            
            async def build_callback(i: discord.Interaction):
                await i.response.edit_message(content="Starting build...", view=SetupProgressView(self.author_id), embed=None)
            async def dryrun_callback(i: discord.Interaction):
                await i.response.edit_message(content="Generating dry run...", view=None, embed=None)
            async def cancel_callback(i: discord.Interaction):
                await i.response.edit_message(content="Setup cancelled.", view=None, embed=None)
                
            build_btn.callback = build_callback
            dryrun_btn.callback = dryrun_callback
            cancel_btn.callback = cancel_callback
            
            self.add_item(build_btn)
            self.add_item(dryrun_btn)
            self.add_item(cancel_btn)
            
            await interaction.response.edit_message(content="Step 4: Review", embed=embed, view=self)

    async def select_features(self, interaction: discord.Interaction):
        # The select is added dynamically, its values are passed in interaction.data
        self.features = interaction.data.get("values", [])
        self.current_step = 3
        await self.update_view(interaction)

    async def select_security(self, interaction: discord.Interaction):
        self.security_level = interaction.data.get("values", [])[0]
        self.current_step = 4
        await self.update_view(interaction)

class SetupProgressView(discord.ui.View):
    __slots__ = ('author_id',)
    
    def __init__(self, author_id: int):
        super().__init__(timeout=300)
        self.author_id = author_id

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelling...", ephemeral=True)
        # Logic to cancel setup

class ServerControlPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Management Sections 1",
        options=[discord.SelectOption(label=opt) for opt in ["Server", "Roles", "Channels", "Permissions", "Tickets", "Moderation", "AutoMod", "Security"]]
    )
    async def sections_1(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.send_message(f"Opened {select.values[0]} section", ephemeral=True)

    @discord.ui.select(
        placeholder="Management Sections 2",
        options=[discord.SelectOption(label=opt) for opt in ["Welcome", "Verification", "Onboarding", "Applications", "Logs", "Backups", "Automation", "Analytics"]]
    )
    async def sections_2(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.send_message(f"Opened {select.values[0]} section", ephemeral=True)

    @discord.ui.button(label="⚡ Full Setup", style=discord.ButtonStyle.success, row=2)
    async def full_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Starting full setup...", ephemeral=True)

    @discord.ui.button(label="🔧 Repair Server", style=discord.ButtonStyle.primary, row=2)
    async def repair(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Repairing server...", ephemeral=True)

    @discord.ui.button(label="💾 Create Backup", style=discord.ButtonStyle.secondary, row=2)
    async def backup(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Creating backup...", ephemeral=True)

    @discord.ui.button(label="🚨 Emergency Lockdown", style=discord.ButtonStyle.danger, row=2)
    async def lockdown(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Lockdown initiated...", ephemeral=True)
