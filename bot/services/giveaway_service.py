import random
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from bot.database.models.giveaways import Giveaway, GiveawayEntry

class GiveawayService:
    def __init__(self, bot):
        self.bot = bot

    async def create_giveaway(
        self, 
        guild_id: int, 
        channel_id: int, 
        host_id: int, 
        prize: str, 
        description: str, 
        winners_count: int, 
        ends_at: datetime, 
        required_role_id: Optional[int] = None
    ) -> Giveaway:
        async with self.bot.db.session() as session:
            giveaway = Giveaway(
                guild_id=guild_id,
                channel_id=channel_id,
                host_id=host_id,
                prize=prize,
                description=description,
                winners_count=winners_count,
                ends_at=ends_at,
                required_role_id=required_role_id
            )
            session.add(giveaway)
            await session.commit()
            return giveaway

    async def enter_giveaway(self, giveaway_id: int, user_id: int) -> bool:
        async with self.bot.db.session() as session:
            entry = GiveawayEntry(giveaway_id=giveaway_id, user_id=user_id)
            session.add(entry)
            try:
                await session.commit()
                return True
            except IntegrityError:
                await session.rollback()
                return False

    async def end_giveaway(self, giveaway_id: int) -> List[int]:
        async with self.bot.db.session() as session:
            stmt = select(Giveaway).where(Giveaway.id == giveaway_id)
            result = await session.execute(stmt)
            giveaway = result.scalar_one_or_none()
            
            if not giveaway or giveaway.ended:
                return []

            giveaway.ended = True
            
            stmt_entries = select(GiveawayEntry.user_id).where(GiveawayEntry.giveaway_id == giveaway_id)
            result_entries = await session.execute(stmt_entries)
            user_ids = [row[0] for row in result_entries.all()]
            
            winners = random.sample(user_ids, min(giveaway.winners_count, len(user_ids))) if user_ids else []
            
            await session.commit()
            return winners

    async def reroll_giveaway(self, giveaway_id: int, count: int = 1) -> List[int]:
        async with self.bot.db.session() as session:
            stmt = select(Giveaway).where(Giveaway.id == giveaway_id)
            result = await session.execute(stmt)
            giveaway = result.scalar_one_or_none()
            
            if not giveaway:
                return []

            stmt_entries = select(GiveawayEntry.user_id).where(GiveawayEntry.giveaway_id == giveaway_id)
            result_entries = await session.execute(stmt_entries)
            user_ids = [row[0] for row in result_entries.all()]
            
            winners = random.sample(user_ids, min(count, len(user_ids))) if user_ids else []
            return winners

    async def get_active_giveaways(self, guild_id: int) -> List[Giveaway]:
        async with self.bot.db.session() as session:
            stmt = select(Giveaway).where(
                Giveaway.guild_id == guild_id,
                Giveaway.ended == False
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_entry_count(self, giveaway_id: int) -> int:
        async with self.bot.db.session() as session:
            stmt = select(func.count(GiveawayEntry.id)).where(GiveawayEntry.giveaway_id == giveaway_id)
            result = await session.execute(stmt)
            return result.scalar_one()
