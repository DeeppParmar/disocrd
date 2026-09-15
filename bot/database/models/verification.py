from sqlalchemy import BigInteger, Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.base import Base

class VerificationConfig(Base):
    __tablename__ = "verification_configs"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    verified_role_id: Mapped[int | None] = mapped_column(BigInteger)
    unverified_role_id: Mapped[int | None] = mapped_column(BigInteger)
    min_account_age_hours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    channel_id: Mapped[int | None] = mapped_column(BigInteger)
    message_id: Mapped[int | None] = mapped_column(BigInteger)
    rules_text: Mapped[str | None] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
