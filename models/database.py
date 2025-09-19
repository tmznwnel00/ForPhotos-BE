"""
SQLAlchemy 데이터베이스 모델 정의
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 설정
    images = relationship("Image", back_populates="user")

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    width = Column(Integer)
    height = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # 관계 설정
    user = relationship("User", back_populates="images")
    analysis_jobs = relationship("AnalysisJob", back_populates="image")

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    job_type = Column(String(50), nullable=False)  # emotion, pose, face, filter
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    execution_time = Column(Float)
    error_message = Column(Text)
    config = Column(JSON)  # 분석 요청 시 사용된 설정

    # 관계 설정
    image = relationship("Image", back_populates="analysis_jobs")
    emotion_results = relationship("EmotionResult", back_populates="analysis_job")
    pose_results = relationship("PoseResult", back_populates="analysis_job")
    face_results = relationship("FaceResult", back_populates="analysis_job")
    filter_results = relationship("FilterResult", back_populates="analysis_job")

class EmotionResult(Base):
    __tablename__ = "emotion_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_job_id = Column(Integer, ForeignKey("analysis_jobs.id"), nullable=False)
    face_id = Column(Integer, nullable=False)
    bbox_x = Column(Float, nullable=False)
    bbox_y = Column(Float, nullable=False)
    bbox_width = Column(Float, nullable=False)
    bbox_height = Column(Float, nullable=False)
    emotion = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    result_image_path = Column(String(500))
    panel_image_path = Column(String(500))

    # 관계 설정
    analysis_job = relationship("AnalysisJob", back_populates="emotion_results")

class PoseResult(Base):
    __tablename__ = "pose_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_job_id = Column(Integer, ForeignKey("analysis_jobs.id"), nullable=False)
    person_id = Column(Integer, nullable=False)
    bbox_x = Column(Float, nullable=False)
    bbox_y = Column(Float, nullable=False)
    bbox_width = Column(Float, nullable=False)
    bbox_height = Column(Float, nullable=False)
    pose_type = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    gender = Column(String(10))
    keypoints = Column(JSON)  # 키포인트 좌표 저장
    result_image_path = Column(String(500))
    analysis_metadata = Column(JSON)

    # 관계 설정
    analysis_job = relationship("AnalysisJob", back_populates="pose_results")

class FaceResult(Base):
    __tablename__ = "face_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_job_id = Column(Integer, ForeignKey("analysis_jobs.id"), nullable=False)
    face_id = Column(Integer, nullable=False)
    bbox_x = Column(Float, nullable=False)
    bbox_y = Column(Float, nullable=False)
    bbox_width = Column(Float, nullable=False)
    bbox_height = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    landmarks = Column(JSON)  # 얼굴 랜드마크 좌표
    result_image_path = Column(String(500))

    # 관계 설정
    analysis_job = relationship("AnalysisJob", back_populates="face_results")

class FilterResult(Base):
    __tablename__ = "filter_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_job_id = Column(Integer, ForeignKey("analysis_jobs.id"), nullable=False)
    filter_type = Column(String(20), nullable=False)
    result_image_path = Column(String(500), nullable=False)

    # 관계 설정
    analysis_job = relationship("AnalysisJob", back_populates="filter_results")