"""
مدل‌های Feedback برای بهبود سیستم
"""
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class QueryFeedback(Base):
    """
    ذخیره feedback کاربران برای بهبود LLM
    """
    __tablename__ = "query_feedback"

    id = Column(Integer, primary_key=True)
    query_id = Column(String(50), unique=True, nullable=False)  # UUID
    
    # سوال و پلن اصلی
    user_question = Column(Text, nullable=False)
    generated_plan = Column(Text, nullable=False)  # JSON as string
    execution_result = Column(Text, nullable=False)  # JSON as string
    
    # Feedback
    feedback_type = Column(String(50), nullable=False)  # "correct", "wrong_result", etc
    user_comment = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<QueryFeedback({self.query_id}, {self.feedback_type})>"
