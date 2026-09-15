from typing import Any, List, Optional
import structlog
from sqlalchemy import select, update

from bot.database.models.suggestions import Suggestion

logger = structlog.get_logger(__name__)

class SuggestionService:
    __slots__ = ('bot',)

    def __init__(self, bot: Any) -> None:
        self.bot = bot

    async def create_suggestion(self, guild_id: int, author_id: int, content: str) -> Suggestion:
        async with self.bot.db.session() as session:
            suggestion = Suggestion(guild_id=guild_id, author_id=author_id, content=content)
            session.add(suggestion)
            await session.commit()
            return suggestion

    async def vote(self, suggestion_id: int, direction: str) -> Optional[Suggestion]:
        async with self.bot.db.session() as session:
            stmt = select(Suggestion).where(Suggestion.id == suggestion_id)
            suggestion = await session.scalar(stmt)
            if not suggestion:
                return None
                
            if direction == 'up':
                suggestion.upvotes = (suggestion.upvotes or 0) + 1
            elif direction == 'down':
                suggestion.downvotes = (suggestion.downvotes or 0) + 1
                
            await session.commit()
            return suggestion

    async def set_status(self, suggestion_id: int, status: str, responder_id: Optional[int] = None, response: Optional[str] = None) -> Optional[Suggestion]:
        async with self.bot.db.session() as session:
            stmt = select(Suggestion).where(Suggestion.id == suggestion_id)
            suggestion = await session.scalar(stmt)
            if not suggestion:
                return None
                
            suggestion.status = status
            suggestion.responder_id = responder_id
            suggestion.response = response
            await session.commit()
            return suggestion

    async def get_suggestions(self, guild_id: int, status: Optional[str] = None, limit: int = 25) -> List[Suggestion]:
        async with self.bot.db.session() as session:
            stmt = select(Suggestion).where(Suggestion.guild_id == guild_id)
            if status:
                stmt = stmt.where(Suggestion.status == status)
            stmt = stmt.order_by(Suggestion.created_at.desc()).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())
