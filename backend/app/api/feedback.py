"""
API برای دریافت Feedback کاربران
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from app.models.feedback import QueryFeedback, FeedbackType
from app.core.database import get_session
import uuid

router = APIRouter(prefix="/api/v1/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    query_id: str  # ID سوالی که feedback داریم
    feedback_type: str  # "correct", "wrong_result", "misunderstood", "suggestion"
    comment: str = None  # نظر اضافی کاربر


@router.post("/submit")
async def submit_feedback(req: FeedbackRequest):
    """
    ذخیره feedback کاربر
    
    مثال:
    ```json
    {
        "query_id": "abc123",
        "feedback_type": "wrong_result",
        "comment": "فاصله غلط محاسبه شد، باید 5 کیلومتر باشه"
    }
    ```
    """
    try:
        # Validate feedback_type
        feedback_type = FeedbackType(req.feedback_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"نوع feedback نامعتبر: {req.feedback_type}")
    
    session = get_session()
    
    try:
        # بررسی اینکه query قبلا ثبت شده؟
        existing = session.query(QueryFeedback).filter(
            QueryFeedback.query_id == req.query_id
        ).first()
        
        if existing:
            # Update existing feedback
            existing.feedback_type = feedback_type
            existing.user_comment = req.comment
        else:
            # نمی‌توانیم query_id جدید ایجاد کنیم، باید از query_execution_service آمده باشه
            raise HTTPException(status_code=404, detail=f"query {req.query_id} یافت نشد")
        
        session.commit()
        
        return {
            "success": True,
            "message": "تشکر از نظر شما! این اطلاعات ما را کمک می‌کند بهتر شویم.",
            "query_id": req.query_id,
            "feedback_type": req.feedback_type,
        }
    
    finally:
        session.close()


@router.get("/stats")
async def get_feedback_stats():
    """آمار feedback‌ها برای تحلیل"""
    session = get_session()
    
    try:
        total = session.query(QueryFeedback).count()
        correct = session.query(QueryFeedback).filter(
            QueryFeedback.feedback_type == FeedbackType.CORRECT
        ).count()
        wrong = session.query(QueryFeedback).filter(
            QueryFeedback.feedback_type == FeedbackType.WRONG_RESULT
        ).count()
        misunderstood = session.query(QueryFeedback).filter(
            QueryFeedback.feedback_type == FeedbackType.MISUNDERSTOOD
        ).count()
        
        return {
            "total_queries": total,
            "correct": correct,
            "wrong_result": wrong,
            "misunderstood": misunderstood,
            "accuracy_rate": f"{(correct / total * 100):.1f}%" if total > 0 else "0%",
        }
    
    finally:
        session.close()
