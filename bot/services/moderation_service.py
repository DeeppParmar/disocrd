import time
from typing import Any, Tuple, List, Optional
from datetime import datetime, timezone

import discord
import structlog
from sqlalchemy import select, update, func, desc

from bot.database.models.moderation import ModerationCase, Warning, CaseNote

logger = structlog.get_logger(__name__)

class ModerationService:
    __slots__ = ('bot',)

    def __init__(self, bot: Any) -> None:
        self.bot = bot

    async def warn(self, guild_id: int, user_id: int, moderator_id: int, reason: str) -> Warning:
        async with self.bot.db.session() as session:
            count_stmt = select(func.count()).select_from(Warning).where(
                Warning.guild_id == guild_id, Warning.user_id == user_id
            )
            current_count = await session.scalar(count_stmt) or 0
            
            warning = Warning(
                guild_id=guild_id,
                user_id=user_id,
                moderator_id=moderator_id,
                reason=reason,
                warning_number=current_count + 1
            )
            session.add(warning)
            await session.commit()
            return warning

    async def get_warnings(self, guild_id: int, user_id: int, active_only: bool = True) -> List[Warning]:
        async with self.bot.db.session() as session:
            stmt = select(Warning).where(Warning.guild_id == guild_id, Warning.user_id == user_id)
            if active_only:
                stmt = stmt.where(Warning.is_active == True)
            stmt = stmt.order_by(Warning.created_at.desc())
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_warning_count(self, guild_id: int, user_id: int) -> int:
        async with self.bot.db.session() as session:
            stmt = select(func.count()).select_from(Warning).where(
                Warning.guild_id == guild_id, Warning.user_id == user_id, Warning.is_active == True
            )
            return await session.scalar(stmt) or 0

    async def create_case(self, guild_id: int, user_id: int, moderator_id: int, action_type: str, reason: str, duration_seconds: Optional[int] = None, evidence: Optional[str] = None) -> ModerationCase:
        async with self.bot.db.session() as session:
            count_stmt = select(func.count()).select_from(ModerationCase).where(ModerationCase.guild_id == guild_id)
            case_number = (await session.scalar(count_stmt) or 0) + 1
            
            expires_at = None
            if duration_seconds:
                expires_at = datetime.fromtimestamp(time.time() + duration_seconds, tz=timezone.utc)
                
            case = ModerationCase(
                guild_id=guild_id,
                case_number=case_number,
                user_id=user_id,
                moderator_id=moderator_id,
                action_type=action_type,
                reason=reason,
                expires_at=expires_at,
                evidence=evidence
            )
            session.add(case)
            await session.commit()
            return case

    async def get_case(self, guild_id: int, case_number: int) -> Optional[ModerationCase]:
        async with self.bot.db.session() as session:
            stmt = select(ModerationCase).where(
                ModerationCase.guild_id == guild_id,
                ModerationCase.case_number == case_number
            )
            return await session.scalar(stmt)

    async def get_user_cases(self, guild_id: int, user_id: int) -> List[ModerationCase]:
        async with self.bot.db.session() as session:
            stmt = select(ModerationCase).where(
                ModerationCase.guild_id == guild_id,
                ModerationCase.user_id == user_id
            ).order_by(desc(ModerationCase.created_at))
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def search_cases(self, guild_id: int, user_id: Optional[int] = None, moderator_id: Optional[int] = None, action_type: Optional[str] = None, limit: int = 25) -> List[ModerationCase]:
        async with self.bot.db.session() as session:
            stmt = select(ModerationCase).where(ModerationCase.guild_id == guild_id)
            if user_id:
                stmt = stmt.where(ModerationCase.user_id == user_id)
            if moderator_id:
                stmt = stmt.where(ModerationCase.moderator_id == moderator_id)
            if action_type:
                stmt = stmt.where(ModerationCase.action_type == action_type)
                
            stmt = stmt.order_by(desc(ModerationCase.created_at)).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def add_case_note(self, case_id: int, author_id: int, content: str) -> CaseNote:
        async with self.bot.db.session() as session:
            note = CaseNote(case_id=case_id, author_id=author_id, content=content)
            session.add(note)
            await session.commit()
            return note

    async def check_escalation(self, guild_id: int, user_id: int, escalation_config: dict) -> Tuple[str, Optional[int]]:
        count = await self.get_warning_count(guild_id, user_id)
        action_str = escalation_config.get(str(count)) or escalation_config.get(count)
        if not action_str:
            return ('notice', None)
            
        parts = action_str.split(':')
        action = parts[0]
        duration = int(parts[1]) if len(parts) > 1 else None
        return (action, duration)

    async def get_active_cases_count(self, guild_id: int) -> int:
        async with self.bot.db.session() as session:
            stmt = select(func.count()).select_from(ModerationCase).where(
                ModerationCase.guild_id == guild_id,
                ModerationCase.is_active == True
            )
            return await session.scalar(stmt) or 0

    async def expire_cases(self, guild_id: int) -> int:
        async with self.bot.db.session() as session:
            stmt = update(ModerationCase).where(
                ModerationCase.guild_id == guild_id,
                ModerationCase.is_active == True,
                ModerationCase.expires_at <= datetime.now(timezone.utc)
            ).values(is_active=False)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount
