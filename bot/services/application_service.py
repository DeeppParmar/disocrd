from typing import Any, List, Dict, Optional
import structlog
from sqlalchemy import select

from bot.database.models.applications import ApplicationConfig, Application, ApplicationResponse

logger = structlog.get_logger(__name__)

class ApplicationService:
    __slots__ = ('bot',)

    def __init__(self, bot: Any) -> None:
        self.bot = bot

    async def create_config(self, guild_id: int, app_type: str, app_name: str, review_channel_id: int, form_fields: dict, result_role_id: Optional[int] = None) -> ApplicationConfig:
        async with self.bot.db.session() as session:
            config = ApplicationConfig(
                guild_id=guild_id,
                app_type=app_type,
                app_name=app_name,
                review_channel_id=review_channel_id,
                form_fields=form_fields,
                result_role_id=result_role_id
            )
            session.add(config)
            await session.commit()
            return config

    async def get_configs(self, guild_id: int) -> List[ApplicationConfig]:
        async with self.bot.db.session() as session:
            stmt = select(ApplicationConfig).where(ApplicationConfig.guild_id == guild_id)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def submit_application(self, config_id: int, guild_id: int, applicant_id: int, responses: Dict[str, Any]) -> Application:
        async with self.bot.db.session() as session:
            app = Application(
                config_id=config_id,
                guild_id=guild_id,
                applicant_id=applicant_id,
                status="pending"
            )
            session.add(app)
            await session.flush()
            
            for field, val in responses.items():
                resp = ApplicationResponse(application_id=app.id, field_name=field, response_value=str(val))
                session.add(resp)
                
            await session.commit()
            return app

    async def review_application(self, app_id: int, reviewer_id: int, status: str, note: Optional[str] = None) -> Optional[Application]:
        async with self.bot.db.session() as session:
            stmt = select(Application).where(Application.id == app_id)
            app = await session.scalar(stmt)
            if not app:
                return None
                
            app.status = status
            app.reviewer_id = reviewer_id
            app.review_note = note
            await session.commit()
            
            if status == "approved":
                config_stmt = select(ApplicationConfig).where(ApplicationConfig.id == app.config_id)
                config = await session.scalar(config_stmt)
                if config and config.result_role_id:
                    guild = self.bot.get_guild(app.guild_id)
                    if guild:
                        member = guild.get_member(app.applicant_id)
                        role = guild.get_role(config.result_role_id)
                        if member and role:
                            try:
                                await member.add_roles(role, reason="Application approved")
                            except Exception:
                                logger.warning(f"Failed to add role {role.id} to {member.id}")
            return app

    async def get_pending(self, guild_id: int) -> List[Application]:
        async with self.bot.db.session() as session:
            stmt = select(Application).where(Application.guild_id == guild_id, Application.status == "pending")
            result = await session.execute(stmt)
            return list(result.scalars().all())
