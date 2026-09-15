from typing import Any, List, Dict, Optional
import structlog
import discord
from datetime import datetime, timezone
from sqlalchemy import select, update

from bot.database.models.analytics import AnalyticsSnapshot

logger = structlog.get_logger(__name__)

class AnalyticsService:
    __slots__ = ('bot',)

    def __init__(self, bot: Any) -> None:
        self.bot = bot

    async def record_snapshot(self, guild_id: int, **stats: Any) -> AnalyticsSnapshot:
        today = datetime.now(timezone.utc).date()
        async with self.bot.db.session() as session:
            stmt = select(AnalyticsSnapshot).where(
                AnalyticsSnapshot.guild_id == guild_id,
                AnalyticsSnapshot.date == today
            )
            snapshot = await session.scalar(stmt)
            
            if not snapshot:
                snapshot = AnalyticsSnapshot(guild_id=guild_id, date=today)
                session.add(snapshot)
                
            for k, v in stats.items():
                if hasattr(snapshot, k):
                    setattr(snapshot, k, v)
                    
            await session.commit()
            return snapshot

    async def get_snapshot(self, guild_id: int, date: Optional[Any] = None) -> Optional[AnalyticsSnapshot]:
        target_date = date or datetime.now(timezone.utc).date()
        async with self.bot.db.session() as session:
            stmt = select(AnalyticsSnapshot).where(
                AnalyticsSnapshot.guild_id == guild_id,
                AnalyticsSnapshot.date == target_date
            )
            return await session.scalar(stmt)

    async def get_snapshots(self, guild_id: int, days: int = 30) -> List[AnalyticsSnapshot]:
        async with self.bot.db.session() as session:
            stmt = select(AnalyticsSnapshot).where(AnalyticsSnapshot.guild_id == guild_id).order_by(AnalyticsSnapshot.date.desc()).limit(days)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_overview(self, guild: discord.Guild) -> Dict[str, Any]:
        return {
            "member_count": guild.member_count,
            "online_count": len([m for m in guild.members if m.status != discord.Status.offline]),
            "channel_count": len(guild.channels),
            "role_count": len(guild.roles),
            "tickets_open": 0, # Should be fetched from ticket service
            "mod_actions_today": 0,
            "raid_risk": "Low"
        }

    async def increment_stat(self, guild_id: int, stat_name: str, amount: int = 1) -> None:
        today = datetime.now(timezone.utc).date()
        async with self.bot.db.session() as session:
            stmt = select(AnalyticsSnapshot).where(
                AnalyticsSnapshot.guild_id == guild_id,
                AnalyticsSnapshot.date == today
            )
            snapshot = await session.scalar(stmt)
            
            if not snapshot:
                snapshot = AnalyticsSnapshot(guild_id=guild_id, date=today)
                session.add(snapshot)
                
            if hasattr(snapshot, stat_name):
                current = getattr(snapshot, stat_name) or 0
                setattr(snapshot, stat_name, current + amount)
                
            await session.commit()
