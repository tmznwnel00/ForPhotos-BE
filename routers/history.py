"""
히스토리 및 결과 조회 API 라우터
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from core.database import get_db
from repositories import (
    UserRepository, ImageRepository, AnalysisJobRepository,
    EmotionResultRepository
)
from routers.auth import get_current_active_user
from models.database import User
from models.database import AnalysisJob

router = APIRouter()

# Response 모델들
class ImageInfo(BaseModel):
    id: int
    filename: str
    original_filename: str
    uploaded_at: datetime
    file_size: int
    width: Optional[int]
    height: Optional[int]

class AnalysisJobInfo(BaseModel):
    id: int
    job_type: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    execution_time: Optional[float]
    error_message: Optional[str]

class EmotionResultInfo(BaseModel):
    id: int
    face_id: int
    bbox: List[float]
    emotion: str
    confidence: float
    result_image_path: Optional[str]
    panel_image_path: Optional[str]

class ImageHistoryResponse(BaseModel):
    image: ImageInfo
    analysis_jobs: List[AnalysisJobInfo]

class EmotionAnalysisHistory(BaseModel):
    job: AnalysisJobInfo
    results: List[EmotionResultInfo]

@router.get("/users/me/images", response_model=List[ImageInfo])
async def get_user_images(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사용자의 업로드 이미지 목록 조회"""
    images = ImageRepository.get_by_user_id(db, current_user.id, skip=skip, limit=limit)
    return [ImageInfo(
        id=img.id,
        filename=img.filename,
        original_filename=img.original_filename,
        uploaded_at=img.uploaded_at,
        file_size=img.file_size,
        width=img.width,
        height=img.height
    ) for img in images]

@router.get("/users/me/history", response_model=List[ImageHistoryResponse])
async def get_user_analysis_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사용자의 분석 히스토리 조회 (이미지별)"""
    images = ImageRepository.get_by_user_id(db, current_user.id, skip=skip, limit=limit)

    history = []
    for image in images:
        jobs = AnalysisJobRepository.get_by_image_id(db, image.id)

        image_info = ImageInfo(
            id=image.id,
            filename=image.filename,
            original_filename=image.original_filename,
            uploaded_at=image.uploaded_at,
            file_size=image.file_size,
            width=image.width,
            height=image.height
        )

        job_infos = [AnalysisJobInfo(
            id=job.id,
            job_type=job.job_type,
            status=job.status,
            started_at=job.started_at,
            completed_at=job.completed_at,
            execution_time=job.execution_time,
            error_message=job.error_message
        ) for job in jobs]

        history.append(ImageHistoryResponse(
            image=image_info,
            analysis_jobs=job_infos
        ))

    return history

@router.get("/images/{image_id}/jobs", response_model=List[AnalysisJobInfo])
async def get_image_analysis_jobs(image_id: int, db: Session = Depends(get_db)):
    """특정 이미지의 분석 작업 목록"""
    image = ImageRepository.get_by_id(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다")

    jobs = AnalysisJobRepository.get_by_image_id(db, image_id)
    return [AnalysisJobInfo(
        id=job.id,
        job_type=job.job_type,
        status=job.status,
        started_at=job.started_at,
        completed_at=job.completed_at,
        execution_time=job.execution_time,
        error_message=job.error_message
    ) for job in jobs]

@router.get("/jobs/{job_id}/emotion-results", response_model=EmotionAnalysisHistory)
async def get_emotion_analysis_results(job_id: int, db: Session = Depends(get_db)):
    """감정 분석 결과 상세 조회"""
    job = AnalysisJobRepository.get_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="분석 작업을 찾을 수 없습니다")

    if job.job_type != "emotion":
        raise HTTPException(status_code=400, detail="감정 분석 작업이 아닙니다")

    results = EmotionResultRepository.get_by_job_id(db, job_id)

    job_info = AnalysisJobInfo(
        id=job.id,
        job_type=job.job_type,
        status=job.status,
        started_at=job.started_at,
        completed_at=job.completed_at,
        execution_time=job.execution_time,
        error_message=job.error_message
    )

    result_infos = [EmotionResultInfo(
        id=result.id,
        face_id=result.face_id,
        bbox=[result.bbox_x, result.bbox_y, result.bbox_width, result.bbox_height],
        emotion=result.emotion,
        confidence=result.confidence,
        result_image_path=result.result_image_path,
        panel_image_path=result.panel_image_path
    ) for result in results]

    return EmotionAnalysisHistory(
        job=job_info,
        results=result_infos
    )

@router.get("/users/me/emotions/stats")
async def get_user_emotion_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사용자의 감정 분석 통계"""
    # 현재는 기본 통계만 제공 (나중에 확장 가능)
    images = ImageRepository.get_by_user_id(db, current_user.id, skip=0, limit=1000)
    total_images = len(images)

    total_jobs = 0
    completed_jobs = 0
    for image in images:
        jobs = AnalysisJobRepository.get_by_image_id(db, image.id)
        emotion_jobs = [job for job in jobs if job.job_type == "emotion"]
        total_jobs += len(emotion_jobs)
        completed_jobs += len([job for job in emotion_jobs if job.status == "completed"])

    return {
        "user_id": current_user.id,
        "total_images": total_images,
        "total_emotion_analyses": total_jobs,
        "completed_analyses": completed_jobs,
        "success_rate": completed_jobs / total_jobs if total_jobs > 0 else 0
    }