from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import select, delete

from bot.database.models.reminders import Reminder

class ReminderService:
    def __init__(self, bot):
        self.bot = bot

    async def create_reminder(self, guild_id: Optional[int], channel_id: int, user_id: int, message: str, remind_at: datetime) -> Reminder:
        async with self.bot.db.session() as session:
            reminder = Reminder(
                guild_id=guild_id,
                channel_id=channel_id,
                user_id=user_id,
                message=message,
                remind_at=remind_at
            )
            session.add(reminder)
            await session.commit()
            return reminder

    async def get_due_reminders(self) -> List[Reminder]:
        async with self.bot.db.session() as session:
            now = datetime.now(timezone.utc)
            stmt = select(Reminder).where(
                Reminder.remind_at <= now,
                Reminder.completed == False
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def complete_reminder(self, reminder_id: int) -> None:
        async with self.bot.db.session() as session:
            stmt = select(Reminder).where(Reminder.id == reminder_id)
            result = await session.execute(stmt)
            reminder = result.scalar_one_or_none()
            if reminder:
                reminder.completed = True
                await session.commit()

    async def get_user_reminders(self, user_id: int, limit: int = 10) -> List[Reminder]:
        async with self.bot.db.session() as session:
            stmt = select(Reminder).where(
                Reminder.user_id == user_id,
                Reminder.completed == False
            ).order_by(Reminder.remind_at.asc()).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def cancel_reminder(self, reminder_id: int, user_id: int) -> bool:
        async with self.bot.db.session() as session:
            stmt = delete(Reminder).where(
                Reminder.id == reminder_id,
                Reminder.user_id == user_id
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
