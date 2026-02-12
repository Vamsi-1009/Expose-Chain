"""
Configuration settings for ExposeChain
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    SHODAN_API_KEY: Optional[str] = None
    VIRUSTOTAL_API_KEY: Optional[str] = None
    HIBP_API_KEY: Optional[str] = None
    
    # JWT Configuration
    JWT_SECRET: str = "default-secret-change-in-production"
    
    # Database
    MONGO_URL: str = "mongodb://localhost:27017/exposechain"
    
    # Application
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    APP_NAME: str = "ExposeChain"
    VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
