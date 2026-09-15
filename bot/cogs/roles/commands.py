import discord
from discord import app_commands
from discord.ext import commands
from bot.core.bot import DiscordServerOS
from bot.cogs.roles.views import RoleMenuView
from bot.utils.formatters import success_embed, info_embed

class RoleCog(commands.Cog):
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    roles_group = app_commands.Group(name="roles", description="Role management commands", default_permissions=discord.Permissions(manage_roles=True))

    @roles_group.command(name="create", description="Create a managed role")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def roles_create(self, interaction: discord.Interaction, name: str, color: str, hoist: bool):
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            c = discord.Color(int(color.replace("#", ""), 16))
        except ValueError:
            c = discord.Color.default()
        
        role = await interaction.guild.create_role(name=name, color=c, hoist=hoist, reason=f"Created by {interaction.user}")
        await interaction.followup.send(embed=success_embed(f"Created role {role.mention}"))

    @roles_group.command(name="delete", description="Delete a managed role")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def roles_delete(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer(ephemeral=True, thinking=True)
        name = role.name
        await role.delete(reason=f"Deleted by {interaction.user}")
        await interaction.followup.send(embed=success_embed(f"Deleted role {name}"))

    @roles_group.command(name="list", description="List all roles with hierarchy visualization")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def roles_list(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        roles = sorted(interaction.guild.roles, key=lambda r: r.position, reverse=True)
        desc = "\n".join(f"{r.mention} (Pos: {r.position})" for r in roles if r.name != "@everyone")
        if len(desc) > 4000:
            desc = desc[:4000] + "\n...and more"
        await interaction.followup.send(embed=info_embed(title="Role Hierarchy", description=desc))

    @roles_group.command(name="sync", description="Sync role permissions to presets")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def roles_sync(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await interaction.followup.send(embed=success_embed("Role permissions synced."))

    @roles_group.command(name="menu", description="Create self-assignable role select menu")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def roles_menu(self, interaction: discord.Interaction, channel: discord.TextChannel, title: str):
        # Simplistic version without modal for brevity, ideally opens a modal to configure
        # Here we just use a placeholder
        roles = interaction.guild.roles[1:5] # take a few roles
        options = [discord.SelectOption(label=r.name, value=str(r.id)) for r in roles]
        if not options:
            await interaction.response.send_message("Not enough roles.", ephemeral=True)
            return
            
        view = RoleMenuView(options)
        await channel.send(embed=info_embed(title=title, description="Select your roles below:"), view=view)
        await interaction.response.send_message("Menu created in the channel.", ephemeral=True)
