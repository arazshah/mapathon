from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os

from database import get_db
from query_engine import process_question

app = FastAPI(
    title="Mapathon API",
    description="API برای پرسش‌های مکانی زبان طبیعی",
    version="1.0.0"
)

# CORS
origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    map: dict
    report: dict

@app.get("/")
async def root():
    return {"message": "Mapathon Backend is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/test")
async def test():
    return {"test": "success", "env": os.getenv("DATABASE_URL", "not set")[:20]}

@app.post("/api/v1/query", response_model=QueryResponse)
async def query(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        result = process_question(db, request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در پردازش درخواست: {str(e)}")
