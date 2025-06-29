"""
Application configuration using Pydantic Settings
"""
from typing import List, Optional
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application settings
    app_name: str = Field(default="RNEP", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # API settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_prefix: str = Field(default="/api", description="API prefix")
    
    # Database settings
    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/rnep_db",
        description="Database connection URL"
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")
    
    # Redis settings
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    redis_ttl: int = Field(default=3600, description="Redis TTL in seconds")
    
    # File storage settings
    upload_dir: Path = Field(
        default=Path("./data/imports"),
        description="Upload directory"
    )
    output_dir: Path = Field(
        default=Path("./data/outputs"),
        description="Output directory"
    )
    max_upload_size: int = Field(
        default=104857600,  # 100MB
        description="Maximum upload file size in bytes"
    )
    
    # External services (will be used when algorithms are ready)
    unist_api_url: Optional[str] = Field(
        default=None,
        description="UNIST API URL"
    )
    unist_api_key: Optional[str] = Field(
        default=None,
        description="UNIST API key"
    )
    konkuk_api_url: Optional[str] = Field(
        default=None,
        description="Konkuk API URL"
    )
    konkuk_api_key: Optional[str] = Field(
        default=None,
        description="Konkuk API key"
    )
    
    # Security settings (for future use)
    secret_key: str = Field(
        default="change-this-in-production",
        description="Secret key for JWT"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration in minutes"
    )
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    
    @validator("upload_dir", "output_dir", pre=True)
    def create_directories(cls, v):
        """Create directories if they don't exist"""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @validator("log_level", pre=True)
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of {valid_levels}")
        return v.upper()


# Global settings instance
settings = Settings()