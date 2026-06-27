"""
Endpoint اصلی: سوال زبان طبیعی → پاسخ + نقشه + گزارش
"""
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.llm_planner import create_plan
from app.core.executor import execute_plan
from app.core.response_builder import build_response

router = APIRouter(prefix="/api/v1", tags=["query"])


class QueryRequest(BaseModel):
    question: str


@router.post("/query")
def query(req: QueryRequest):
    """سوال زبان طبیعی → plan → اجرا → contract استاندارد"""
    question = req.question.strip()
    if not question:
        return {
            "success": False, "question": question,
            "answer": None, "map": None, "report": None,
            "error": "سوال خالی است",
        }

    plan = create_plan(question)
    exec_result = execute_plan(plan)
    return build_response(question, plan, exec_result)
