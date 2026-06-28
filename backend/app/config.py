"""
تنظیمات تطبیق‌پذیر برای Mapathon
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # OpenAI / LLM
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Database - PostgreSQL برای داده‌های مکانی
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/mapathon"
    )
    
    # Database - SQLite برای feedback
    feedback_db_url: str = os.getenv(
        "FEEDBACK_DB_URL",
        "sqlite:///./data/mapathon_feedback.db"
    )
    
    # Server
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # Dashboard
    dashboard_password: str = os.getenv("DASHBOARD_PASSWORD", "admin")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

settings = Settings()
