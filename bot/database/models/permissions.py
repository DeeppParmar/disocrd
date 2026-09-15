from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.base import Base

class PermissionPolicy(Base):
    __tablename__ = "permission_policies"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    channel_id: Mapped[int | None] = mapped_column(BigInteger)
    role_id: Mapped[int | None] = mapped_column(BigInteger)
    allow_bits: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    deny_bits: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    policy_name: Mapped[str] = mapped_column(String(100), nullable=False)
    managed_by_bot: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
