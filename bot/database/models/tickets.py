from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text, SmallInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
import datetime

from bot.database.base import Base

class TicketConfig(Base):
    __tablename__ = "ticket_configs"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    ticket_type: Mapped[str] = mapped_column(String(50), nullable=False)
    category_id: Mapped[int | None] = mapped_column(BigInteger)
    log_channel_id: Mapped[int | None] = mapped_column(BigInteger)
    staff_roles: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    max_open_per_user: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    inactivity_hours: Mapped[int] = mapped_column(Integer, default=24, nullable=False)
    auto_close_hours: Mapped[int] = mapped_column(Integer, default=48, nullable=False)
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    form_fields: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

class Ticket(Base):
    __tablename__ = "tickets"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    channel_id: Mapped[int | None] = mapped_column(BigInteger)
    creator_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    claimed_by: Mapped[int | None] = mapped_column(BigInteger)
    ticket_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    priority: Mapped[str] = mapped_column(String(10), default="normal", nullable=False)
    ticket_number: Mapped[int] = mapped_column(Integer, nullable=False)
    subject: Mapped[str | None] = mapped_column(String(256))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    closed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    transcript_url: Mapped[str | None] = mapped_column(Text)
    rating: Mapped[int | None] = mapped_column(SmallInteger)
    feedback: Mapped[str | None] = mapped_column(Text)

class TicketMember(Base):
    __tablename__ = "ticket_members"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    role_type: Mapped[str] = mapped_column(String(20), nullable=False)
    added_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
