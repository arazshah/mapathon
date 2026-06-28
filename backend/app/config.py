import os
from functools import lru_cache

class Settings:
    """
    تنظیمات مرکزی بک‌اند
    """
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        # مسیر دیتابیس SQLite برای نظرات
        self.database_path = os.getenv("DATABASE_PATH", "data/mapathon_feedback.db")
        
        # رمز عبور داشبورد
        self.dashboard_password = os.getenv("DASHBOARD_PASSWORD", "admin")
        
        # تنظیمات CORS
        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
