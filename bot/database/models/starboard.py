from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, Boolean, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.base import Base

class StarboardConfig(Base):
    """Configuration for a guild's starboard."""
    __tablename__ = 'starboard_configs'

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    emoji: Mapped[str] = mapped_column(String(50), default='⭐', nullable=False)
    threshold: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    self_star: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

class StarboardEntry(Base):
    """Represents a message posted to the starboard."""
    __tablename__ = 'starboard_entries'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('starboard_configs.guild_id', ondelete='CASCADE'), index=True, nullable=False)
    original_message_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    starboard_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    author_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    star_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
