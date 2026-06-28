import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# ============================================================
# دیتابیس SQLite برای نظرات کاربران (feedback)
# ============================================================
FEEDBACK_DATABASE_URL = f"sqlite:///{settings.feedback_db_path}"

os.makedirs(os.path.dirname(settings.feedback_db_path), exist_ok=True)

feedback_engine = create_engine(
    FEEDBACK_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

FeedbackSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=feedback_engine)

Base = declarative_base()


def get_db():
    """اتصال به دیتابیس نظرات (SQLite)"""
    db = FeedbackSessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """ساخت جداول نظرات"""
    Base.metadata.create_all(bind=feedback_engine)


# ============================================================
# دیتابیس PostgreSQL + PostGIS برای داده‌های OSM
# ============================================================
postgis_engine = None
PostgisSessionLocal = None

if settings.postgis_url:
    postgis_engine = create_engine(settings.postgis_url, echo=False, pool_pre_ping=True)
    PostgisSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=postgis_engine)


def get_postgis_db():
    """اتصال به دیتابیس OSM (PostGIS)"""
    if PostgisSessionLocal is None:
        raise RuntimeError("اتصال PostGIS تنظیم نشده است. متغیر POSTGIS_URL را تنظیم کنید.")
    db = PostgisSessionLocal()
    try:
        yield db
    finally:
        db.close()
