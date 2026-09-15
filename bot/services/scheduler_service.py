from typing import Any, List, Optional
from datetime import datetime, timezone
import structlog
from sqlalchemy import select, text, delete

from bot.database.models.automation import ScheduledTask

logger = structlog.get_logger(__name__)

class SchedulerService:
    __slots__ = ('bot',)

    def __init__(self, bot: Any) -> None:
        self.bot = bot

    async def schedule_task(self, guild_id: int, task_type: str, payload: dict, run_at: Optional[datetime] = None, cron: Optional[str] = None) -> ScheduledTask:
        async with self.bot.db.session() as session:
            task = ScheduledTask(
                guild_id=guild_id,
                task_type=task_type,
                payload=payload,
                run_at=run_at or datetime.now(timezone.utc),
                cron_expression=cron,
                status="pending"
            )
            session.add(task)
            await session.commit()
            return task

    async def poll_due_tasks(self, limit: int = 10) -> List[ScheduledTask]:
        async with self.bot.db.session() as session:
            stmt = select(ScheduledTask).where(
                ScheduledTask.status == "pending",
                ScheduledTask.run_at <= datetime.now(timezone.utc)
            ).limit(limit).with_for_update(skip_locked=True)
            result = await session.execute(stmt)
            tasks = list(result.scalars().all())
            return tasks

    async def complete_task(self, task_id: int) -> None:
        async with self.bot.db.session() as session:
            stmt = select(ScheduledTask).where(ScheduledTask.id == task_id)
            task = await session.scalar(stmt)
            if task:
                if task.cron_expression:
                    pass # Calculate next run based on cron and update run_at
                else:
                    task.status = "completed"
                await session.commit()

    async def fail_task(self, task_id: int) -> None:
        async with self.bot.db.session() as session:
            stmt = select(ScheduledTask).where(ScheduledTask.id == task_id)
            task = await session.scalar(stmt)
            if task:
                task.retry_count = (task.retry_count or 0) + 1
                if task.retry_count >= (task.max_retries or 3):
                    task.status = "failed"
                await session.commit()

    async def dispatch_task(self, task: ScheduledTask) -> None:
        logger.info(f"Dispatching task {task.id} of type {task.task_type}")
        # Handlers implementation routing
        try:
            if task.task_type == 'unban':
                pass
            elif task.task_type == 'close_ticket':
                pass
            await self.complete_task(task.id)
        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            await self.fail_task(task.id)

    async def cancel_task(self, task_id: int) -> None:
        async with self.bot.db.session() as session:
            stmt = delete(ScheduledTask).where(ScheduledTask.id == task_id)
            await session.execute(stmt)
            await session.commit()

    async def get_guild_tasks(self, guild_id: int) -> List[ScheduledTask]:
        async with self.bot.db.session() as session:
            stmt = select(ScheduledTask).where(ScheduledTask.guild_id == guild_id)
            result = await session.execute(stmt)
            return list(result.scalars().all())
