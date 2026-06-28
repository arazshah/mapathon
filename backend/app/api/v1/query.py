from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_postgis_db
from app.core.executor import execute_plan

router = APIRouter(tags=["query"])


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    success: bool
    type: str | None = None
    message: str
    center: dict | None = None
    places: list | None = None
    count: int | None = None
    distance_meters: float | None = None
    area_m2: float | None = None
    plan: dict | None = None
    error: str | None = None


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest, db: Session = Depends(get_postgis_db)):
    """
    دریافت سوال زبان طبیعی و پاسخ GIS از PostGIS
    """
    try:
        result = execute_plan(request.question, db)
        return QueryResponse(**result)
    except Exception as e:
        return QueryResponse(
            success=False,
            type="error",
            message="خطا در پردازش سوال",
            error=str(e),
        )
