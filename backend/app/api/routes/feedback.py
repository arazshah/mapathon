from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.feedback import Feedback

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackCreate(BaseModel):
    query_id: Optional[str] = None
    query_text: Optional[str] = None
    feedback_type: Literal["correct", "wrong_result", "misunderstood", "suggestion"]
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    query_id: Optional[str]
    query_text: Optional[str]
    feedback_type: str
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    """
    ثبت نظر جدید
    """
    db_feedback = Feedback(
        query_id=feedback.query_id,
        query_text=feedback.query_text,
        feedback_type=feedback.feedback_type,
        comment=feedback.comment,
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


@router.get("/", response_model=list[FeedbackResponse])
def list_feedback(limit: int = 100, db: Session = Depends(get_db)):
    """
    دریافت لیست نظرات
    """
    return db.query(Feedback).order_by(Feedback.created_at.desc()).limit(limit).all()


@router.get("/stats")
def feedback_stats(db: Session = Depends(get_db)):
    """
    آمار کلی نظرات
    """
    total = db.query(Feedback).count()
    by_type = {}
    for row in db.query(Feedback.feedback_type).all():
        by_type[row.feedback_type] = by_type.get(row.feedback_type, 0) + 1

    return {
        "total": total,
        "by_type": by_type,
    }
