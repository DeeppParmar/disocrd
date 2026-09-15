from sqlalchemy import BigInteger, Date, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
import datetime

from bot.database.base import Base

class AnalyticsSnapshot(Base):
    __tablename__ = "analytics_snapshots"
    __table_args__ = (
        UniqueConstraint("guild_id", "snapshot_date", name="uq_analytics_snapshots_guild_date"),
    )
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    member_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    online_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    new_joins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    leaves: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    messages_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tickets_opened: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tickets_closed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mod_actions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    channel_activity: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    role_distribution: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
