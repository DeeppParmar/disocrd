from typing import Any, List, Optional
import structlog
from sqlalchemy import select

from bot.database.models.reports import Report

logger = structlog.get_logger(__name__)

class ReportService:
    __slots__ = ('bot',)

    def __init__(self, bot: Any) -> None:
        self.bot = bot

    async def create_report(self, guild_id: int, reporter_id: int, target_id: int, report_type: str, description: str, message_id: Optional[int] = None) -> Report:
        async with self.bot.db.session() as session:
            report = Report(
                guild_id=guild_id,
                reporter_id=reporter_id,
                target_id=target_id,
                report_type=report_type,
                description=description,
                message_id=message_id,
                status="open"
            )
            session.add(report)
            await session.commit()
            return report

    async def get_open_reports(self, guild_id: int) -> List[Report]:
        async with self.bot.db.session() as session:
            stmt = select(Report).where(Report.guild_id == guild_id, Report.status == "open")
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def resolve_report(self, report_id: int, handler_id: int, resolution: str) -> Optional[Report]:
        async with self.bot.db.session() as session:
            stmt = select(Report).where(Report.id == report_id)
            report = await session.scalar(stmt)
            if not report:
                return None
                
            report.status = "resolved"
            report.handler_id = handler_id
            report.resolution = resolution
            await session.commit()
            return report

    async def dismiss_report(self, report_id: int, handler_id: int) -> Optional[Report]:
        async with self.bot.db.session() as session:
            stmt = select(Report).where(Report.id == report_id)
            report = await session.scalar(stmt)
            if not report:
                return None
                
            report.status = "dismissed"
            report.handler_id = handler_id
            await session.commit()
            return report
