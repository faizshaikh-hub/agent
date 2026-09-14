"""
Application configuration loaded from environment variables.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # Groq API
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "gemma2-9b-it"
    GROQ_FALLBACK_MODEL: str = "llama-3.3-70b-versatile"

    # Database
    DATABASE_URL: str = "sqlite:///./complaint_mgmt.db"

    # App
    APP_NAME: str = "AIVOA Complaint Management System"
    DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
