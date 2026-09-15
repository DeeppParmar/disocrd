from typing import Any, List, Optional
import discord
import structlog
from sqlalchemy import select, desc
from datetime import datetime, timezone

from bot.database.models.logging import LogEvent, SecurityEvent
from bot.database.models.guild import GuildConfig
from bot.core.constants import Colors

logger = structlog.get_logger(__name__)

class LoggingService:
    __slots__ = ('bot',)

    def __init__(self, bot: Any) -> None:
        self.bot = bot

    async def log_event(self, guild_id: int, event_type: str, category: str, actor_id: Optional[int] = None, target_id: Optional[int] = None, channel_id: Optional[int] = None, details: Optional[dict] = None) -> LogEvent:
        async with self.bot.db.session() as session:
            event = LogEvent(
                guild_id=guild_id,
                event_type=event_type,
                category=category,
                actor_id=actor_id,
                target_id=target_id,
                channel_id=channel_id,
                details=details or {}
            )
            session.add(event)
            await session.commit()
            
        embed = await self.build_log_embed(event)
        await self.send_to_log_channel(guild_id, category, embed)
        return event

    async def log_security_event(self, guild_id: int, event_type: str, severity: str, details: Optional[dict] = None) -> SecurityEvent:
        async with self.bot.db.session() as session:
            event = SecurityEvent(
                guild_id=guild_id,
                event_type=event_type,
                severity=severity,
                details=details or {}
            )
            session.add(event)
            await session.commit()
            
        if severity in ('high', 'critical'):
            embed = discord.Embed(title=f"Security Alert: {event_type}", color=discord.Color.red())
            if details:
                for k, v in details.items():
                    embed.add_field(name=k, value=str(v)[:1024])
            await self.send_to_log_channel(guild_id, 'security', embed)
            
        return event

    async def get_events(self, guild_id: int, category: Optional[str] = None, limit: int = 50, before: Optional[datetime] = None) -> List[LogEvent]:
        async with self.bot.db.session() as session:
            stmt = select(LogEvent).where(LogEvent.guild_id == guild_id)
            if category:
                stmt = stmt.where(LogEvent.category == category)
            if before:
                stmt = stmt.where(LogEvent.created_at < before)
            stmt = stmt.order_by(desc(LogEvent.created_at)).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_security_events(self, guild_id: int, resolved: Optional[bool] = None, severity: Optional[str] = None, limit: int = 50) -> List[SecurityEvent]:
        async with self.bot.db.session() as session:
            stmt = select(SecurityEvent).where(SecurityEvent.guild_id == guild_id)
            if resolved is not None:
                stmt = stmt.where(SecurityEvent.resolved == resolved)
            if severity:
                stmt = stmt.where(SecurityEvent.severity == severity)
            stmt = stmt.order_by(desc(SecurityEvent.created_at)).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def resolve_security_event(self, event_id: int) -> Optional[SecurityEvent]:
        async with self.bot.db.session() as session:
            stmt = select(SecurityEvent).where(SecurityEvent.id == event_id)
            event = await session.scalar(stmt)
            if event:
                event.resolved = True
                await session.commit()
            return event

    async def build_log_embed(self, event: LogEvent) -> discord.Embed:
        embed = discord.Embed(title=f"Log: {event.event_type}", timestamp=event.created_at or datetime.now(timezone.utc))
        if event.actor_id:
            embed.add_field(name="Actor", value=f"<@{event.actor_id}>", inline=True)
        if event.target_id:
            embed.add_field(name="Target", value=f"<@{event.target_id}>", inline=True)
        if event.channel_id:
            embed.add_field(name="Channel", value=f"<#{event.channel_id}>", inline=True)
        
        if event.details:
            desc = ""
            for k, v in event.details.items():
                desc += f"**{k}**: {v}\n"
            if desc:
                embed.description = desc[:4096]
                
        return embed

    async def send_to_log_channel(self, guild_id: int, category: str, embed: discord.Embed) -> None:
        async with self.bot.db.session() as session:
            stmt = select(GuildConfig).where(GuildConfig.guild_id == guild_id)
            config = await session.scalar(stmt)
            if not config or not config.log_channels:
                return
                
            channel_id = config.log_channels.get(category)
            if not channel_id:
                return
                
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return
            
        channel = guild.get_channel(channel_id)
        if channel and isinstance(channel, discord.TextChannel):
            try:
                await channel.send(embed=embed)
            except discord.HTTPException:
                logger.warning(f"Failed to send log to {channel_id} in {guild_id}")
