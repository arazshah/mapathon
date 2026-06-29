from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Any
import json

from app.core.database import get_db
from app.models.feedback import Feedback
from app.config import settings

router = APIRouter(tags=["feedback"])


def verify_dashboard_password(x_dashboard_password: Optional[str] = Header(None)):
    """بررسی رمز عبور داشبورد از هدر"""
    if x_dashboard_password != settings.dashboard_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="دسترسی غیرمجاز",
        )
    return True


# ============================================================
# ورود به داشبورد
# ============================================================
class LoginRequest(BaseModel):
    password: str


@router.post("/feedback/login")
def login(req: LoginRequest):
    """بررسی رمز عبور و بازگرداندن token (همان رمز برای سادگی)"""
    if req.password == settings.dashboard_password:
        return {
            "success": True,
            "token": settings.dashboard_password,
            "message": "ورود موفق",
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="رمز عبور نادرست است",
    )


# ============================================================
# ثبت نظر
# ============================================================
class FeedbackCreate(BaseModel):
    query_id: Optional[str] = None
    user_question: Optional[str] = None
    generated_plan: Optional[Any] = None
    execution_result: Optional[Any] = None
    feedback_type: str
    comment: Optional[str] = None


@router.post("/feedback/submit", status_code=status.HTTP_201_CREATED)
def submit_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    """ثبت نظر جدید کاربر"""
    plan_str = (
        json.dumps(feedback.generated_plan, ensure_ascii=False)
        if feedback.generated_plan else None
    )
    result_str = (
        json.dumps(feedback.execution_result, ensure_ascii=False)
        if feedback.execution_result else None
    )

    db_feedback = Feedback(
        query_id=feedback.query_id,
        question=feedback.user_question,
        generated_plan=plan_str,
        execution_result=result_str,
        feedback_type=feedback.feedback_type,
        comment=feedback.comment,
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)

    return {
        "success": True,
        "message": "نظر شما ثبت شد. متشکریم!",
        "id": db_feedback.id,
    }


# ============================================================
# آمار نظرات (داشبورد)
# ============================================================
@router.get("/feedback/stats")
def feedback_stats(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_dashboard_password),
):
    """آمار کلی برای داشبورد"""
    total = db.query(Feedback).count()

    by_type = {}
    for row in db.query(Feedback.feedback_type).all():
        by_type[row.feedback_type] = by_type.get(row.feedback_type, 0) + 1

    correct = by_type.get("correct", 0)
    wrong = by_type.get("wrong_result", 0)
    misunderstood = by_type.get("misunderstood", 0)
    suggestion = by_type.get("suggestion", 0)

    # محاسبه نرخ دقت: صحیح / (صحیح + نادرست + اشتباه فهمیده)
    evaluated = correct + wrong + misunderstood
    accuracy = (correct / evaluated * 100) if evaluated > 0 else 0

    return {
        "total_queries": total,
        "correct": correct,
        "wrong_result": wrong,
        "misunderstood": misunderstood,
        "suggestion": suggestion,
        "accuracy_rate": f"{accuracy:.0f}%",
    }


# ============================================================
# نظرات اخیر (داشبورد)
# ============================================================
@router.get("/feedback/recent")
def recent_feedback(
    limit: int = 20,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_dashboard_password),
):
    """آخرین نظرات برای داشبورد"""
    rows = (
        db.query(Feedback)
        .order_by(Feedback.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "feedbacks": [
            {
                "id": r.id,
                "question": r.question,
                "feedback_type": r.feedback_type,
                "comment": r.comment,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]
    }