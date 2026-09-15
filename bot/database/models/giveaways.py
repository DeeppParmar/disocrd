from datetime import datetime
from sqlalchemy import BigInteger, String, Text, Integer, Boolean, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.base import Base

class Giveaway(Base):
    """Represents a giveaway in a guild."""
    __tablename__ = 'giveaways'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    host_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    prize: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    winners_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    required_role_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class GiveawayEntry(Base):
    """Represents a user's entry in a giveaway."""
    __tablename__ = 'giveaway_entries'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    giveaway_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('giveaways.id', ondelete='CASCADE'), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    entered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('giveaway_id', 'user_id', name='uq_giveaway_user'),
    )
