import discord
from discord import app_commands
from discord.ext import commands

from bot.core.bot import DiscordServerOS
from bot.utils.formatters import info_embed

class FunCog(commands.GroupCog, group_name="utility"):
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    @app_commands.command(name="userinfo", description="Get detailed user info")
    @app_commands.guild_only()
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        
        embed = info_embed(f"User Info for {user.display_name}")
        embed.set_thumbnail(url=user.display_avatar.url)
        
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(user.created_at, "R"), inline=True)
        embed.add_field(name="Joined", value=discord.utils.format_dt(user.joined_at, "R") if user.joined_at else "Unknown", inline=True)
        
        roles = [r.mention for r in user.roles[1:]] # exclude @everyone
        roles_str = " ".join(roles) if roles else "None"
        if len(roles_str) > 1024:
            roles_str = roles_str[:1021] + "..."
            
        embed.add_field(name=f"Roles [{len(roles)}]", value=roles_str, inline=False)
        
        if user.premium_since:
            embed.add_field(name="Boosting Since", value=discord.utils.format_dt(user.premium_since, "R"), inline=False)
            
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Get detailed server info")
    @app_commands.guild_only()
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        embed = info_embed(f"Server Info for {guild.name}")
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.banner:
            embed.set_image(url=guild.banner.url)
            
        embed.add_field(name="Owner", value=f"<@{guild.owner_id}>", inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(guild.created_at, "R"), inline=True)
        embed.add_field(name="Members", value=str(guild.member_count), inline=True)
        
        embed.add_field(name="Channels", value=f"Text: {len(guild.text_channels)}\nVoice: {len(guild.voice_channels)}\nCategories: {len(guild.categories)}", inline=True)
        embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="Boost Level", value=f"Level {guild.premium_tier} ({guild.premium_subscription_count} boosts)", inline=True)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Show a user's avatar")
    @app_commands.guild_only()
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        
        embed = discord.Embed(title=f"{user.display_name}'s Avatar", color=discord.Color.blurple())
        embed.set_image(url=user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="banner", description="Show a user's banner")
    @app_commands.guild_only()
    async def banner(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        
        # We need to fetch the user to get their banner
        fetched_user = await self.bot.fetch_user(user.id)
        
        if not fetched_user.banner:
            await interaction.response.send_message(f"{user.display_name} does not have a banner.", ephemeral=True)
            return
            
        embed = discord.Embed(title=f"{user.display_name}'s Banner", color=discord.Color.blurple())
        embed.set_image(url=fetched_user.banner.url)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roleinfo", description="Get detailed role info")
    @app_commands.guild_only()
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        embed = info_embed(f"Role Info for {role.name}")
        if role.icon:
            embed.set_thumbnail(url=role.icon.url)
            
        embed.add_field(name="ID", value=role.id, inline=True)
        embed.add_field(name="Color", value=str(role.color), inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(role.created_at, "R"), inline=True)
        
        embed.add_field(name="Hoisted", value="Yes" if role.hoist else "No", inline=True)
        embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No", inline=True)
        embed.add_field(name="Members", value=str(len(role.members)), inline=True)
        
        await interaction.response.send_message(embed=embed)
