"""Application configuration using Pydantic settings.

This module manages all configuration for the ReefConnect backend, loading from environment
variables with validation. It supports both monolith and microservices deployment modes, allowing
for flexible configuration based on the deployment context.
"""

import os
import secrets
from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# TODO: Consider adopting ENV_FILE selector approach for simplifying handling of dev/stage/prod vars
# as the project grows. For now, the current setup is sufficient for early development/deployment.

# Determine deployment mode and env files dynamically
DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "monolith")

# Detect component directory (e.g., 'api_service', 'media_worker')
# Assumes this script is run from a component's directory or backend root
current_dir = os.path.basename(os.getcwd())
if current_dir in ["api_service", "media_worker", "ml_tagger_worker", "materialized_data_worker"]:
    component = current_dir
else:
    component = None  # Running from backend root or unknown

if DEPLOYMENT_MODE == "monolith":
    # Monolith mode: load backend shared + monolith-specific
    ENV_FILES = ["backend/.env", "backend/.env.monolith"]
elif DEPLOYMENT_MODE == "microservices":
    # Microservices mode: load component-specific + backend shared
    if component:
        ENV_FILES = [f"backend/{component}/.env", "backend/.env"]
    else:
        ENV_FILES = "backend/.env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Uses Pydantic's BaseSettings to automatically load and validate
    configuration from environment variables or .env file(s).
    """

    model_config = SettingsConfigDict(
        env_file=ENV_FILES,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Deployment Mode
    DEPLOYMENT_MODE: Literal["monolith", "microservices"] = "monolith"

    # Application Settings
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "ReefConnect API"
    VERSION: str = "0.1.0"

    # Database Configuration
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql+asyncpg://reefconnect:password@localhost:5432/reefconnect_dev",
        description="Async database URL for SQLAlchemy (asyncpg driver)"
    )
    DATABASE_SYNC_URL: PostgresDsn = Field(
        default="postgresql+psycopg2://reefconnect:password@localhost:5432/reefconnect_dev",
        description="Sync database URL for Alembic migrations (psycopg2 driver)"
    )

    # Database Pool Settings
    DB_POOL_SIZE: int = Field(default=5, ge=1, le=100)
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0, le=100)
    DB_POOL_TIMEOUT: int = Field(default=30, ge=1, le=300)
    DB_ECHO: bool = Field(default=False, description="Echo SQL statements to logs")

    # JWT Authentication
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for JWT encoding/decoding"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1, le=1440)

    # CORS Settings
    BACKEND_CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="List of allowed CORS origins"
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            # Handle JSON string format from env var
            if v.startswith("["):
                import json
                return json.loads(v)
            # Handle comma-separated string
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # PostgreSQL Direct Connection Settings (for Docker/external tools)
    POSTGRES_USER: str = "reefconnect"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "reefconnect_dev"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    @property
    def database_url_str(self) -> str:
        """Get database URL as string for SQLAlchemy."""
        return str(self.DATABASE_URL)

    @property
    def database_sync_url_str(self) -> str:
        """Get sync database URL as string for Alembic."""
        return str(self.DATABASE_SYNC_URL)

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Dependency for FastAPI to inject settings.

    Returns:
        Settings instance with current configuration

    Example:
        @app.get("/config")
        def get_config(settings: Settings = Depends(get_settings)):
            return {"environment": settings.ENVIRONMENT}
    """
    return settings
