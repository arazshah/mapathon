from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from app.core.database import Base


class Feedback(Base):
    """
    مدل نظرات کاربران
    """
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    query_id = Column(String, nullable=True, index=True)
    query_text = Column(Text, nullable=True)
    feedback_type = Column(String, nullable=False, index=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
