from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(String, nullable=True)
    question = Column(Text, nullable=True)
    generated_plan = Column(Text, nullable=True)
    execution_result = Column(Text, nullable=True)
    feedback_type = Column(String, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())