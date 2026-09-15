"""Configuration settings for the bot using Pydantic BaseSettings."""

from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""
    
    DISCORD_TOKEN: SecretStr
    DISCORD_CLIENT_ID: int
    DISCORD_CLIENT_SECRET: SecretStr
    DATABASE_URL: str
    UPSTASH_REDIS_URL: str
    ENVIRONMENT: Literal["development", "production"] = "development"
    LOG_LEVEL: str = "INFO"
    DEV_GUILD_ID: int | None = None
    SHARD_COUNT: int = 1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
