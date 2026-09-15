from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.base import Base

class AFKStatus(Base):
    """Represents a user's AFK status in a guild."""
    __tablename__ = 'afk_statuses'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reason: Mapped[str] = mapped_column(String(200), default='AFK', nullable=False)
    set_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('guild_id', 'user_id', name='uq_afk_guild_user'),
    )
