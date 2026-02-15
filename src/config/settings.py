"""
Configuration settings for ExposeChain
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List, Union
import os


class Settings(BaseSettings):
    """Application settings"""
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields from .env file
    )

    # CORS Configuration (comma-separated string in .env)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000,http://127.0.0.1:3000"

    # Application Settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    APP_NAME: str = "ExposeChain"
    VERSION: str = "1.0.0"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True

    # MaxMind GeoIP Database Path
    GEOIP_DB_PATH: Optional[str] = "./data/GeoLite2-City.mmdb"

    def get_cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string to list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return []


# Global settings instance
settings = Settings()
