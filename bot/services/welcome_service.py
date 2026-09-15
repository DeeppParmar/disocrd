from typing import Any, Dict, Optional
import discord
import structlog
from sqlalchemy import select, update

from bot.database.models.guild import GuildConfig

logger = structlog.get_logger(__name__)

class WelcomeService:
    __slots__ = ('bot',)

    def __init__(self, bot: Any) -> None:
        self.bot = bot

    async def send_welcome(self, member: discord.Member) -> None:
        async with self.bot.db.session() as session:
            stmt = select(GuildConfig).where(GuildConfig.guild_id == member.guild.id)
            config = await session.scalar(stmt)
            
            if not config or not config.welcome_channel_id:
                return
                
        channel = member.guild.get_channel(config.welcome_channel_id)
        if not channel or not isinstance(channel, discord.TextChannel):
            return
            
        embed = await self.build_welcome_embed(member, config.welcome_message or {})
        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            logger.warning(f"Failed to send welcome message for {member.id} in {member.guild.id}")
            
        # Optional DM welcome would go here based on config flag

    async def build_welcome_embed(self, member: discord.Member, config: Dict[str, Any]) -> discord.Embed:
        guild = member.guild
        replacements = {
            "{user}": str(member),
            "{server}": guild.name,
            "{member_count}": str(guild.member_count),
            "{user.mention}": member.mention
        }
        
        title = config.get("title", "Welcome to {server}!")
        desc = config.get("description", "Welcome {user.mention}!")
        
        for k, v in replacements.items():
            title = title.replace(k, v)
            desc = desc.replace(k, v)
            
        embed = discord.Embed(
            title=title,
            description=desc,
            color=config.get("color", discord.Color.blue().value)
        )
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        elif guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
            
        return embed

    async def update_welcome_config(self, guild_id: int, **config: Any) -> GuildConfig:
        async with self.bot.db.session() as session:
            stmt = select(GuildConfig).where(GuildConfig.guild_id == guild_id)
            guild_config = await session.scalar(stmt)
            
            if not guild_config:
                guild_config = GuildConfig(guild_id=guild_id)
                session.add(guild_config)
                
            for k, v in config.items():
                if hasattr(guild_config, k):
                    setattr(guild_config, k, v)
                    
            await session.commit()
            return guild_config
