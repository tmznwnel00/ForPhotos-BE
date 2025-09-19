"""
애플리케이션 설정
"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # CORS 설정
    ALLOWED_ORIGINS: List[str] = ["*"]

    # 파일 설정
    UPLOAD_DIR: str = "./storage/uploads"
    OUTPUT_DIR: str = "./storage/outputs"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".bmp"]

    # AI 모델 설정
    EMOTION_MODEL: str = "enet_b2_8"
    EMOTION_DEVICE: str = "auto"  # auto, cuda, cpu
    EMOJI_DIR: str = "../emotion/examples/emojis"

    # 포즈 분석 설정
    YOLO_MODEL_PATH: str = "../pose/yolov8n.pt"
    FACE_MIN_CONF: float = 0.25

    # 데이터베이스 설정
    DATABASE_URL: str = "sqlite:///./storage/forphotos.db"
    DATABASE_ECHO: bool = False

    # 인증 설정
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()