from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
import datetime

from bot.database.base import Base

class Guild(Base):
    __tablename__ = "guilds"
    
    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    bot_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())

class GuildConfig(Base):
    __tablename__ = "guild_configs"
    
    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    server_type: Mapped[str | None] = mapped_column(String(20))
    features_enabled: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    prefix: Mapped[str] = mapped_column(String(10), default="!", nullable=False)
    locale: Mapped[str] = mapped_column(String(5), default="en", nullable=False)
    
    mod_log_channel_id: Mapped[int | None] = mapped_column(BigInteger)
    security_log_channel_id: Mapped[int | None] = mapped_column(BigInteger)
    welcome_channel_id: Mapped[int | None] = mapped_column(BigInteger)
    rules_channel_id: Mapped[int | None] = mapped_column(BigInteger)
    ticket_log_channel_id: Mapped[int | None] = mapped_column(BigInteger)
    suggestion_channel_id: Mapped[int | None] = mapped_column(BigInteger)
    report_channel_id: Mapped[int | None] = mapped_column(BigInteger)
    
    staff_role_ids: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    mod_role_ids: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    admin_role_ids: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    
    config_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    setup_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    setup_phase: Mapped[str | None] = mapped_column(String(20))
    health_score: Mapped[int | None] = mapped_column(Integer)
    last_health_check: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
