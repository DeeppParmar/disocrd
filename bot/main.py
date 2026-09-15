"""Main entry point for the Discord Server OS bot."""

import asyncio
import logging
import sys

from redis.asyncio import Redis
import structlog

from bot.config.settings import Settings
from bot.core.bot import DiscordServerOS
from bot.database.engine import DatabaseManager


def configure_logging(settings: Settings) -> None:
    """Configure structlog based on environment.
    
    Args:
        settings: Application configuration.
    """
    is_prod = settings.ENVIRONMENT == "production"
    
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if is_prod:
        processors.append(structlog.processors.dict_tracebacks)
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
        
    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )
    
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


async def main() -> None:
    """Async entrypoint for the application."""
    settings = Settings()
    configure_logging(settings)
    
    logger = structlog.get_logger(__name__)
    logger.info("Starting Discord Server OS", environment=settings.ENVIRONMENT)
    
    db = DatabaseManager(settings.DATABASE_URL)
    
    redis_client = Redis.from_url(
        settings.UPSTASH_REDIS_URL,
        decode_responses=True
    )
    
    bot = DiscordServerOS(settings=settings, db=db, redis=redis_client)
    
    try:
        await bot.start(settings.DISCORD_TOKEN.get_secret_value())
    except Exception as e:
        logger.exception("Fatal error occurred", error=e)
    finally:
        if not bot.is_closed():
            await bot.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
