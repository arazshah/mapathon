from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.database import init_db
from app.api.v1.query import router as query_router
from app.api.routes.feedback import router as feedback_router

app = FastAPI(
    title="Mapathon API",
    description="API برای سوالات مکانی زبان طبیعی",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# راه‌اندازی دیتابیس در استارت اپ
@app.on_event("startup")
def on_startup():
    init_db()


# روترها
app.include_router(query_router, prefix="/api/v1")
app.include_router(feedback_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "Mapathon API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
