from typing import Any, Optional
import discord
import structlog
from datetime import datetime, timezone
from sqlalchemy import select

from bot.database.models.verification import VerificationConfig

logger = structlog.get_logger(__name__)

class VerificationService:
    __slots__ = ('bot',)

    def __init__(self, bot: Any) -> None:
        self.bot = bot

    async def get_config(self, guild_id: int) -> Optional[VerificationConfig]:
        async with self.bot.db.session() as session:
            stmt = select(VerificationConfig).where(VerificationConfig.guild_id == guild_id)
            return await session.scalar(stmt)

    async def setup_verification(self, guild_id: int, mode: str, verified_role_id: int, channel_id: Optional[int] = None, **kwargs: Any) -> VerificationConfig:
        async with self.bot.db.session() as session:
            stmt = select(VerificationConfig).where(VerificationConfig.guild_id == guild_id)
            config = await session.scalar(stmt)
            
            if not config:
                config = VerificationConfig(guild_id=guild_id)
                session.add(config)
                
            config.mode = mode
            config.verified_role_id = verified_role_id
            if channel_id:
                config.channel_id = channel_id
                
            for k, v in kwargs.items():
                if hasattr(config, k):
                    setattr(config, k, v)
                    
            await session.commit()
            return config

    async def verify_member(self, guild: discord.Guild, member: discord.Member, config: VerificationConfig) -> bool:
        if config.min_account_age_hours > 0:
            if not await self.check_account_age(member, config.min_account_age_hours):
                return False
                
        roles_to_add = []
        verified_role = guild.get_role(config.verified_role_id)
        if verified_role:
            roles_to_add.append(verified_role)
            
        roles_to_remove = []
        if config.unverified_role_id:
            unverified_role = guild.get_role(config.unverified_role_id)
            if unverified_role and unverified_role in member.roles:
                roles_to_remove.append(unverified_role)
                
        try:
            if roles_to_add:
                await member.add_roles(*roles_to_add, reason="Verification complete")
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove, reason="Verification complete")
            return True
        except discord.HTTPException:
            logger.warning(f"Failed to verify member {member.id} in guild {guild.id}")
            return False

    async def check_account_age(self, member: discord.Member, min_hours: int) -> bool:
        age = datetime.now(timezone.utc) - member.created_at
        return age.total_seconds() / 3600 >= min_hours
