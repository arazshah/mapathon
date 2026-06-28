from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.query import router as query_router
from app.api.routes.feedback import router as feedback_router, engine
from app.models.feedback import Base

app = FastAPI(title="Mapathon API")

# ساخت خودکار جداول دیتابیس (از جمله query_feedback)
Base.metadata.create_all(bind=engine)

# ✅ CORS برای Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://192.168.1.104:3000",
        "https://mapathon.ir",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router‌ها
app.include_router(query_router)
app.include_router(feedback_router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
