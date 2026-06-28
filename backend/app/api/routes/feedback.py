"""
API برای دریافت Feedback کاربران + داشبورد محافظت‌شده
"""
import os
from typing import Optional
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models.feedback import QueryFeedback
from app.config import settings

router = APIRouter(prefix="/api/v1/feedback", tags=["feedback"])

DATABASE_URL = settings.feedback_db_url

if DATABASE_URL.startswith("sqlite:///./"):
    db_path = DATABASE_URL.replace("sqlite:///./", "")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

DASHBOARD_PASSWORD = settings.dashboard_password


def verify_password(x_dashboard_password: str = Header(None)):
    """بررسی رمز عبور داشبورد از هدر"""
    if x_dashboard_password != DASHBOARD_PASSWORD:
        raise HTTPException(status_code=401, detail="رمز عبور نادرست است")
    return True


class FeedbackRequest(BaseModel):
    query_id: str
    user_question: str
    generated_plan: dict
    execution_result: dict
    feedback_type: str
    comment: Optional[str] = None


class LoginRequest(BaseModel):
    password: str


@router.post("/login")
async def login(req: LoginRequest):
    """ورود به داشبورد"""
    if req.password == DASHBOARD_PASSWORD:
        return {"success": True, "token": DASHBOARD_PASSWORD}
    raise HTTPException(status_code=401, detail="رمز عبور نادرست است")


@router.post("/submit")
async def submit_feedback(req: FeedbackRequest):
    """ذخیره feedback کاربر (عمومی - بدون رمز)"""
    valid_types = ["correct", "wrong_result", "misunderstood", "suggestion"]
    if req.feedback_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"نوع feedback نامعتبر: {req.feedback_type}")

    session = Session(engine)
    try:
        existing = session.query(QueryFeedback).filter(
            QueryFeedback.query_id == req.query_id
        ).first()

        if existing:
            existing.feedback_type = req.feedback_type
            existing.user_comment = req.comment
            existing.created_at = datetime.utcnow()
        else:
            feedback = QueryFeedback(
                query_id=req.query_id,
                user_question=req.user_question,
                generated_plan=json.dumps(req.generated_plan, ensure_ascii=False),
                execution_result=json.dumps(req.execution_result, ensure_ascii=False),
                feedback_type=req.feedback_type,
                user_comment=req.comment,
            )
            session.add(feedback)
        session.commit()
        return {
            "success": True,
            "message": "✅ تشکر از نظر شما!",
            "query_id": req.query_id,
        }
    except Exception as e:
        session.rollback()
        return {"success": False, "error": str(e)}
    finally:
        session.close()


@router.get("/stats")
async def get_feedback_stats(_: bool = Depends(verify_password)):
    """آمار feedback (محافظت‌شده با رمز)"""
    session = Session(engine)
    try:
        total = session.query(QueryFeedback).count()
        if total == 0:
            return {
                "total_queries": 0, "correct": 0, "wrong_result": 0,
                "misunderstood": 0, "suggestion": 0, "accuracy_rate": "0%",
            }
        correct = session.query(QueryFeedback).filter(QueryFeedback.feedback_type == "correct").count()
        wrong = session.query(QueryFeedback).filter(QueryFeedback.feedback_type == "wrong_result").count()
        misunderstood = session.query(QueryFeedback).filter(QueryFeedback.feedback_type == "misunderstood").count()
        suggestion = session.query(QueryFeedback).filter(QueryFeedback.feedback_type == "suggestion").count()
        return {
            "total_queries": total, "correct": correct, "wrong_result": wrong,
            "misunderstood": misunderstood, "suggestion": suggestion,
            "accuracy_rate": f"{(correct / total * 100):.1f}%",
        }
    finally:
        session.close()


@router.get("/recent")
async def get_recent_feedback(limit: int = 20, _: bool = Depends(verify_password)):
    """آخرین feedback‌ها (محافظت‌شده با رمز)"""
    session = Session(engine)
    try:
        feedbacks = session.query(QueryFeedback).order_by(
            QueryFeedback.created_at.desc()
        ).limit(limit).all()
        return {
            "success": True,
            "count": len(feedbacks),
            "feedbacks": [
                {
                    "query_id": f.query_id,
                    "question": f.user_question,
                    "feedback_type": f.feedback_type,
                    "comment": f.user_comment,
                    "created_at": f.created_at.isoformat(),
                }
                for f in feedbacks
            ],
        }
    finally:
        session.close()
