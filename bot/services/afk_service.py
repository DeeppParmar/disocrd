from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert

from bot.database.models.afk import AFKStatus

class AFKService:
    def __init__(self, bot):
        self.bot = bot

    async def set_afk(self, guild_id: int, user_id: int, reason: str = 'AFK') -> AFKStatus:
        async with self.bot.db.session() as session:
            stmt = insert(AFKStatus).values(
                guild_id=guild_id,
                user_id=user_id,
                reason=reason
            ).on_conflict_do_update(
                index_elements=['guild_id', 'user_id'],
                set_={'reason': reason}
            )
            await session.execute(stmt)
            await session.commit()

            stmt2 = select(AFKStatus).where(
                AFKStatus.guild_id == guild_id,
                AFKStatus.user_id == user_id
            )
            result = await session.execute(stmt2)
            return result.scalar_one()

    async def remove_afk(self, guild_id: int, user_id: int) -> bool:
        async with self.bot.db.session() as session:
            stmt = delete(AFKStatus).where(
                AFKStatus.guild_id == guild_id,
                AFKStatus.user_id == user_id
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def get_afk(self, guild_id: int, user_id: int) -> Optional[AFKStatus]:
        async with self.bot.db.session() as session:
            stmt = select(AFKStatus).where(
                AFKStatus.guild_id == guild_id,
                AFKStatus.user_id == user_id
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def check_mentions(self, guild_id: int, mentioned_ids: List[int]) -> List[AFKStatus]:
        if not mentioned_ids:
            return []
            
        async with self.bot.db.session() as session:
            stmt = select(AFKStatus).where(
                AFKStatus.guild_id == guild_id,
                AFKStatus.user_id.in_(mentioned_ids)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
