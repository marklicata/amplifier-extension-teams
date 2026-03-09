"""Configuration management for the Amplifier Teams Bot."""

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Amplifier API settings
    amplifier_api_url: str = Field(..., description="Base URL for the Amplifier API")
    amplifier_api_key: str = Field(..., description="API key for authenticating with Amplifier")
    amplifier_base_config_id: str = Field(..., description="Default config ID for sessions")
    amplifier_base_config_name: str = Field(
        default="chat-bundle", description="Name of the base config"
    )

    # Teams Bot credentials (uses managed identity for auth)
    microsoft_app_id: str = Field(..., description="Microsoft App ID from Azure Bot registration")
    
    microsoft_app_type: str = Field(default="MultiTenant", description="Bot app type")
    microsoft_app_tenant_id: str | None = Field(
        default=None, description="Tenant ID for SingleTenant bots"
    )

    # Service configuration
    bot_service_url: str = Field(
        default="http://localhost:3978", description="Public URL where bot is accessible"
    )
    port: int = Field(default=3978, description="Port for the bot service")

    # Session management
    session_timeout_minutes: int = Field(
        default=60, description="Minutes before inactive session expires"
    )
    max_sessions_per_user: int = Field(
        default=10, description="Maximum concurrent sessions per user"
    )


# Global settings instance
settings = Settings()
