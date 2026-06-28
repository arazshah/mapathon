import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# ساخت URL دیتابیس SQLite
DATABASE_URL = f"sqlite:///{settings.database_path}"

# اطمینان از وجود پوشه دیتا
os.makedirs(os.path.dirname(settings.database_path), exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    وابستگی FastAPI برای دریافت Session دیتابیس
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    ساخت جداول در صورت عدم وجود
    """
    Base.metadata.create_all(bind=engine)
