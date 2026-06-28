from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.database import init_db
from app.api.v1.query import router as query_router
from app.api.routes.feedback import router as feedback_router

# غیرفعال کردن ریدایرکت خودکار اسلش انتهایی
app = FastAPI(
    title="Mapathon API",
    description="API برای سوالات مکانی زبان طبیعی",
    version="1.0.0",
    redirect_slashes=False,
)

# تنظیم CORS صحیح
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mapathon.ir",
        "https://www.mapathon.ir",
        "https://api.mapathon.ir",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

# راه‌اندازی دیتابیس در استارت اپ
@app.on_event("startup")
def on_startup():
    init_db()


# روترها - مسیر بدون اسلش انتهایی
app.include_router(query_router, prefix="/api/v1")
app.include_router(feedback_router, prefix="/api/v1")


@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc):
    return JSONResponse(
        status_code=405,
        content={"detail": "Method not allowed"},
        headers={"Access-Control-Allow-Origin": "*"},
    )


@app.get("/")
def root():
    return {"message": "Mapathon API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
