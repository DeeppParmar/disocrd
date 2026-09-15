from sqlalchemy import BigInteger, Boolean, DateTime, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
import datetime

from bot.database.base import Base

class RoleMapping(Base):
    __tablename__ = "role_mappings"
    __table_args__ = (
        UniqueConstraint("guild_id", "discord_role_id", name="uq_role_mappings_guild_discord"),
    )
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    discord_role_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    logical_name: Mapped[str] = mapped_column(String(100), nullable=False)
    template_id: Mapped[str | None] = mapped_column(String(50))
    managed_by_bot: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    permissions_preset: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class RoleMenu(Base):
    __tablename__ = "role_menus"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    menu_type: Mapped[str] = mapped_column(String(20), nullable=False) # 'select' or 'button'
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    roles: Mapped[list[dict]] = mapped_column(JSONB, nullable=False) # [{role_id, label, emoji, description}]
    max_selections: Mapped[int] = mapped_column(BigInteger, default=25, nullable=False)
    mutually_exclusive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    staff_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
