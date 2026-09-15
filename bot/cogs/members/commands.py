import discord
from discord import app_commands
from discord.ext import commands
import structlog
from datetime import datetime, timezone

from bot.core.bot import DiscordServerOS
from bot.utils.formatters import info_embed
from bot.utils.checks import is_staff

log = structlog.get_logger()

class MemberCog(commands.Cog):
    """Handles member information."""
    
    __slots__ = ('bot',)

    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    member_group = app_commands.Group(name="member", description="Member commands")

    @member_group.command(name="info", description="Get detailed member profile")
    @app_commands.guild_only()
    async def member_info(self, interaction: discord.Interaction, user: discord.Member) -> None:
        await interaction.response.defer(ephemeral=True)
        
        join_date = user.joined_at
        created_at = user.created_at
        
        embed = info_embed(
            title=f"Member Info: {user.display_name}",
            description=f"Detailed profile for {user.mention}"
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Account Created", value=discord.utils.format_dt(created_at, style='R'))
        embed.add_field(name="Joined Server", value=discord.utils.format_dt(join_date, style='R') if join_date else "Unknown")
        
        roles = [r.mention for r in reversed(user.roles[1:])]
        roles_str = " ".join(roles) if roles else "None"
        if len(roles_str) > 1024:
            roles_str = roles_str[:1021] + "..."
            
        embed.add_field(name="Roles", value=roles_str, inline=False)
        embed.add_field(name="Top Role", value=user.top_role.mention, inline=False)
        
        # Simulate DB fetches for warnings and tickets
        warnings = 0
        tickets = 0
        embed.add_field(name="Warnings", value=str(warnings))
        embed.add_field(name="Tickets", value=str(tickets))
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @member_group.command(name="search", description="Search for members")
    @app_commands.guild_only()
    @is_staff()
    async def member_search(self, interaction: discord.Interaction, query: str) -> None:
        await interaction.response.defer(ephemeral=True)
        
        query = query.lower()
        matches = [m for m in interaction.guild.members if query in m.name.lower() or (m.nick and query in m.nick.lower())]
        
        if not matches:
            return await interaction.followup.send(embed=info_embed("Search Results", f"No members found matching `{query}`."), ephemeral=True)
            
        desc = "\n".join(f"{m.mention} ({m.id})" for m in matches[:10])
        if len(matches) > 10:
            desc += f"\n*...and {len(matches) - 10} more.*"
            
        embed = info_embed(title=f"Search Results for '{query}'", description=desc)
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(MemberCog(bot))
