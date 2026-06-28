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
        origins = os.getenv("CORS_ORIGINS", "")
        if origins:
            self.cors_origins = [o.strip() for o in origins.split(",") if o.strip()]
        else:
            self.cors_origins = [
                "https://mapathon.ir",
                "https://www.mapathon.ir",
                "https://api.mapathon.ir",
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ]

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
