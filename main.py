"""
ForPhotos-ML Backend API Server
FastAPI 기반 이미지 분석 API 서버
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from routers import emotion, pose, filter, face, user, history, auth
from core.config import settings
from utils.db_init import init_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 초기화
    print("🚀 Starting ForPhotos-ML API Server")
    print("📊 Initializing database...")
    init_database()
    print("📋 Loading AI models...")
    yield
    # 종료 시 정리
    print("🔄 Shutting down...")

app = FastAPI(
    title="ForPhotos-ML API",
    description="AI-powered photo analysis and enhancement API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 설정
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
app.mount("/files", StaticFiles(directory=settings.OUTPUT_DIR), name="files")

# 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(user.router, prefix="/api", tags=["user"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(emotion.router, prefix="/api/emotion", tags=["emotion"])
app.include_router(pose.router, prefix="/api/pose", tags=["pose"])
app.include_router(filter.router, prefix="/api/filter", tags=["filter"])
app.include_router(face.router, prefix="/api/face", tags=["face"])

@app.get("/")
async def root():
    return {
        "message": "ForPhotos-ML API Server",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )