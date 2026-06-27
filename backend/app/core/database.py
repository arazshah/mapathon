from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings

# ساخت engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,   # چک کردن اتصال قبل از استفاده
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency برای استفاده در endpoint ها"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_connection() -> dict:
    """تست اتصال به دیتابیس و PostGIS"""
    try:
        with engine.connect() as conn:
            # تست اتصال
            conn.execute(text("SELECT 1"))
            # تست PostGIS
            result = conn.execute(text("SELECT PostGIS_Version()"))
            postgis_version = result.scalar()
            return {
                "connected": True,
                "postgis_version": postgis_version,
            }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
        }
