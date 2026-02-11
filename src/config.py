"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Central configuration for ExposeChain."""

    # Application
    app_name: str = "ExposeChain"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = Field(
        default="sqlite:///exposechain.db",
        description="Database connection string (SQLite default, PostgreSQL supported)",
    )

    # Kubernetes
    k8s_in_cluster: bool = Field(
        default=False,
        description="Whether running inside a K8s cluster",
    )
    k8s_kubeconfig: str | None = Field(
        default=None,
        description="Path to kubeconfig file (None = default location)",
    )
    k8s_context: str | None = Field(
        default=None,
        description="Kubernetes context to use",
    )

    # AWS
    aws_region: str = Field(default="us-east-1")
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None

    # Scanning
    scan_interval_seconds: int = Field(
        default=300,
        description="Interval between automatic scans in seconds",
    )

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    model_config = {"env_file": ".env", "env_prefix": "EXPOSE_"}


settings = Settings()
