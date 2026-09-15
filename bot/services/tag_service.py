from typing import Optional, List
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.tags import Tag

class TagService:
    def __init__(self, bot):
        self.bot = bot

    async def create_tag(self, guild_id: int, name: str, content: str, author_id: int) -> Optional[Tag]:
        async with self.bot.db.session() as session:
            # Check for existing tag case insensitively
            stmt = select(Tag).where(
                Tag.guild_id == guild_id,
                func.lower(Tag.name) == name.lower()
            )
            result = await session.execute(stmt)
            if result.scalar_one_or_none():
                return None

            tag = Tag(
                guild_id=guild_id,
                name=name,
                content=content,
                author_id=author_id
            )
            session.add(tag)
            await session.commit()
            return tag

    async def get_tag(self, guild_id: int, name: str) -> Optional[Tag]:
        async with self.bot.db.session() as session:
            stmt = select(Tag).where(
                Tag.guild_id == guild_id,
                func.lower(Tag.name) == name.lower()
            )
            result = await session.execute(stmt)
            tag = result.scalar_one_or_none()
            if tag:
                tag.uses += 1
                await session.commit()
            return tag

    async def delete_tag(self, guild_id: int, name: str) -> bool:
        async with self.bot.db.session() as session:
            stmt = delete(Tag).where(
                Tag.guild_id == guild_id,
                func.lower(Tag.name) == name.lower()
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def update_tag(self, guild_id: int, name: str, content: str) -> Optional[Tag]:
        async with self.bot.db.session() as session:
            stmt = select(Tag).where(
                Tag.guild_id == guild_id,
                func.lower(Tag.name) == name.lower()
            )
            result = await session.execute(stmt)
            tag = result.scalar_one_or_none()
            if tag:
                tag.content = content
                await session.commit()
                return tag
            return None

    async def list_tags(self, guild_id: int, limit: int = 25) -> List[Tag]:
        async with self.bot.db.session() as session:
            stmt = select(Tag).where(Tag.guild_id == guild_id).order_by(Tag.uses.desc()).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def search_tags(self, guild_id: int, query: str) -> List[Tag]:
        async with self.bot.db.session() as session:
            stmt = select(Tag).where(
                Tag.guild_id == guild_id,
                Tag.name.ilike(f"%{query}%")
            ).limit(25)
            result = await session.execute(stmt)
            return list(result.scalars().all())
