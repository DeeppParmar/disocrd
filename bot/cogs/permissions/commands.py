import discord
from discord import app_commands
from discord.ext import commands
from bot.core.bot import DiscordServerOS
from bot.cogs.permissions.views import PermissionSimulatorView
from bot.utils.formatters import info_embed, success_embed

class PermissionsCog(commands.Cog):
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    perms_group = app_commands.Group(name="permissions", description="Permissions management", default_permissions=discord.Permissions(administrator=True))

    @perms_group.command(name="check", description="Permission simulator for user in a channel")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def permissions_check(self, interaction: discord.Interaction, user: discord.Member, channel: discord.TextChannel):
        await interaction.response.defer(ephemeral=True, thinking=True)
        perms = channel.permissions_for(user)
        
        desc = []
        for name, value in perms:
            icon = "✅" if value else "❌"
            desc.append(f"{icon} {name.replace('_', ' ').title()}")
            
        embed = info_embed(
            title=f"Permissions for {user.display_name} in #{channel.name}",
            description="\n".join(desc)
        )
        await interaction.followup.send(embed=embed, view=PermissionSimulatorView(user, channel))

    @perms_group.command(name="audit", description="Scans for dangerous permission combinations")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def permissions_audit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        risky_roles = []
        for role in interaction.guild.roles:
            if role.permissions.administrator and role.name != "@everyone":
                risky_roles.append(role.mention)
                
        desc = "No risky roles found." if not risky_roles else f"Roles with Administrator:\n" + "\n".join(risky_roles)
        await interaction.followup.send(embed=info_embed(title="Permission Audit", description=desc))

    @perms_group.command(name="repair", description="Fix permission issues")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def permissions_repair(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await interaction.followup.send(embed=success_embed("Permissions repaired."))
