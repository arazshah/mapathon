from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.v1.query import router as query_router
from app.api.routes.feedback import router as feedback_router

app = FastAPI(
    title="Mapathon API",
    description="API برای پرسش‌های مکانی زبان طبیعی",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Mapathon Backend is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/test")
async def test():
    return {"test": "success", "env": os.getenv("DATABASE_URL", "not set")[:20]}

app.include_router(query_router, tags=["query"])
app.include_router(feedback_router, tags=["feedback"])
