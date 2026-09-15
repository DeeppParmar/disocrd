from datetime import datetime
from sqlalchemy import BigInteger, String, Text, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.base import Base

class Tag(Base):
    """Represents a tag in a guild."""
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    uses: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    __table_args__ = (
        UniqueConstraint('guild_id', 'name', name='uq_tag_guild_name'),
    )
