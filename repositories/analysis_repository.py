"""
분석 작업 및 결과 CRUD 작업
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from models.database import (
    AnalysisJob, EmotionResult, PoseResult,
    FaceResult, FilterResult
)
from datetime import datetime

class AnalysisJobRepository:
    """AnalysisJob 테이블 CRUD 작업"""

    @staticmethod
    def create(
        db: Session,
        image_id: int,
        job_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> AnalysisJob:
        """새 분석 작업 생성"""
        db_job = AnalysisJob(
            image_id=image_id,
            job_type=job_type,
            status="pending",
            config=config
        )
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        return db_job

    @staticmethod
    def get_by_id(db: Session, job_id: int) -> Optional[AnalysisJob]:
        """ID로 분석 작업 조회"""
        return db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()

    @staticmethod
    def update_status(
        db: Session,
        job_id: int,
        status: str,
        execution_time: Optional[float] = None,
        error_message: Optional[str] = None
    ) -> Optional[AnalysisJob]:
        """분석 작업 상태 업데이트"""
        db_job = AnalysisJobRepository.get_by_id(db, job_id)
        if not db_job:
            return None

        db_job.status = status
        if execution_time is not None:
            db_job.execution_time = execution_time
        if error_message is not None:
            db_job.error_message = error_message
        if status == "completed":
            db_job.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(db_job)
        return db_job

    @staticmethod
    def get_by_image_id(db: Session, image_id: int) -> List[AnalysisJob]:
        """이미지별 분석 작업 목록"""
        return db.query(AnalysisJob)\
            .filter(AnalysisJob.image_id == image_id)\
            .order_by(AnalysisJob.started_at.desc())\
            .all()


class EmotionResultRepository:
    """EmotionResult 테이블 CRUD 작업"""

    @staticmethod
    def create(
        db: Session,
        analysis_job_id: int,
        face_id: int,
        bbox_x: float,
        bbox_y: float,
        bbox_width: float,
        bbox_height: float,
        emotion: str,
        confidence: float,
        result_image_path: Optional[str] = None,
        panel_image_path: Optional[str] = None
    ) -> EmotionResult:
        """감정 분석 결과 생성"""
        db_result = EmotionResult(
            analysis_job_id=analysis_job_id,
            face_id=face_id,
            bbox_x=bbox_x,
            bbox_y=bbox_y,
            bbox_width=bbox_width,
            bbox_height=bbox_height,
            emotion=emotion,
            confidence=confidence,
            result_image_path=result_image_path,
            panel_image_path=panel_image_path
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return db_result

    @staticmethod
    def get_by_job_id(db: Session, job_id: int) -> List[EmotionResult]:
        """분석 작업별 감정 결과 조회"""
        return db.query(EmotionResult)\
            .filter(EmotionResult.analysis_job_id == job_id)\
            .all()


class PoseResultRepository:
    """PoseResult 테이블 CRUD 작업"""

    @staticmethod
    def create(
        db: Session,
        analysis_job_id: int,
        person_id: int,
        bbox_x: float,
        bbox_y: float,
        bbox_width: float,
        bbox_height: float,
        pose_type: str,
        confidence: float,
        gender: Optional[str] = None,
        keypoints: Optional[List] = None,
        result_image_path: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> PoseResult:
        """포즈 분석 결과 생성"""
        db_result = PoseResult(
            analysis_job_id=analysis_job_id,
            person_id=person_id,
            bbox_x=bbox_x,
            bbox_y=bbox_y,
            bbox_width=bbox_width,
            bbox_height=bbox_height,
            pose_type=pose_type,
            confidence=confidence,
            gender=gender,
            keypoints=keypoints,
            result_image_path=result_image_path,
            metadata=metadata
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return db_result

    @staticmethod
    def get_by_job_id(db: Session, job_id: int) -> List[PoseResult]:
        """분석 작업별 포즈 결과 조회"""
        return db.query(PoseResult)\
            .filter(PoseResult.analysis_job_id == job_id)\
            .all()


class FaceResultRepository:
    """FaceResult 테이블 CRUD 작업"""

    @staticmethod
    def create(
        db: Session,
        analysis_job_id: int,
        face_id: int,
        bbox_x: float,
        bbox_y: float,
        bbox_width: float,
        bbox_height: float,
        confidence: float,
        landmarks: Optional[List] = None,
        result_image_path: Optional[str] = None
    ) -> FaceResult:
        """얼굴 검출 결과 생성"""
        db_result = FaceResult(
            analysis_job_id=analysis_job_id,
            face_id=face_id,
            bbox_x=bbox_x,
            bbox_y=bbox_y,
            bbox_width=bbox_width,
            bbox_height=bbox_height,
            confidence=confidence,
            landmarks=landmarks,
            result_image_path=result_image_path
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return db_result

    @staticmethod
    def get_by_job_id(db: Session, job_id: int) -> List[FaceResult]:
        """분석 작업별 얼굴 검출 결과 조회"""
        return db.query(FaceResult)\
            .filter(FaceResult.analysis_job_id == job_id)\
            .all()


class FilterResultRepository:
    """FilterResult 테이블 CRUD 작업"""

    @staticmethod
    def create(
        db: Session,
        analysis_job_id: int,
        filter_type: str,
        result_image_path: str
    ) -> FilterResult:
        """필터 적용 결과 생성"""
        db_result = FilterResult(
            analysis_job_id=analysis_job_id,
            filter_type=filter_type,
            result_image_path=result_image_path
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return db_result

    @staticmethod
    def get_by_job_id(db: Session, job_id: int) -> Optional[FilterResult]:
        """분석 작업별 필터 결과 조회"""
        return db.query(FilterResult)\
            .filter(FilterResult.analysis_job_id == job_id)\
            .first()