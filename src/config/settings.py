"""
Configuration settings for ExposeChain
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings"""

    # Database Configuration (Supabase PostgreSQL)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/exposechain"
    )

    # Supabase Optional Keys
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None

    # CORS Configuration (Parse comma-separated string)
    CORS_ORIGINS: List[str] = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse CORS_ORIGINS from environment if provided as comma-separated string
        cors_env = os.getenv("CORS_ORIGINS", "")
        if cors_env:
            self.CORS_ORIGINS = [origin.strip() for origin in cors_env.split(",")]
        elif not self.CORS_ORIGINS:
            # Default CORS origins for development
            self.CORS_ORIGINS = [
                "http://localhost:3000",
                "http://localhost:8000",
                "http://127.0.0.1:8000",
                "http://127.0.0.1:3000"
            ]

    # Application Settings
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    APP_NAME: str = "ExposeChain"
    VERSION: str = "1.0.0"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True

    # MaxMind GeoIP Database Path
    GEOIP_DB_PATH: Optional[str] = "./data/GeoLite2-City.mmdb"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
