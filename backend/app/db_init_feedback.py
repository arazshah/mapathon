"""
مقدار دهی اولیه Feedback Database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from app.models.feedback import Base
import sqlite3

DATABASE_URL = "sqlite:///./mapathon_feedback.db"

def init_feedback_db():
    """ایجاد جداول Feedback در SQLite"""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("✅ Feedback database initialized at mapathon_feedback.db")

if __name__ == "__main__":
    init_feedback_db()
