"""
얼굴 검출 API 라우터
"""

import time
import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session

from models.schemas import (
    FaceDetectionRequest,
    FaceDetectionResponse,
    ResponseFormat,
    Face
)
from services.face_service import face_service
from utils.file_handler import file_handler
from core.database import get_db
from repositories import (
    UserRepository, ImageRepository, AnalysisJobRepository, FaceResultRepository
)
from routers.auth import get_current_active_user
from models.database import User

router = APIRouter()

@router.post("/detect", response_model=FaceDetectionResponse)
async def detect_faces(
    file: UploadFile = File(...),
    min_confidence: float = Form(0.5),
    response_format: ResponseFormat = Form(ResponseFormat.URL),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    얼굴 검출

    - **file**: 업로드할 이미지 파일
    - **Authorization**: Bearer 토큰 (헤더)
    - **min_confidence**: 최소 검출 신뢰도 (0.0-1.0)
    - **response_format**: 응답 형식 (base64 또는 url)
    """
    start_time = time.time()
    temp_files = []

    try:
        # 현재 사용자 (토큰으로 인증됨)
        user_id = current_user.id

        # 파일 업로드
        input_path = await file_handler.save_upload_file(file)
        temp_files.append(input_path)

        # 이미지 DB 저장
        file_stat = os.stat(input_path)
        db_image = ImageRepository.create(
            db=db,
            user_id=current_user.id,
            filename=os.path.basename(input_path),
            original_filename=file.filename,
            file_path=input_path,
            file_size=file_stat.st_size,
            mime_type=file.content_type or "image/jpeg"
        )

        # 분석 작업 생성
        config = {
            "min_confidence": min_confidence,
            "response_format": response_format
        }
        analysis_job = AnalysisJobRepository.create(
            db=db,
            image_id=db_image.id,
            job_type="face",
            config=config
        )

        # 분석 작업 상태 업데이트 (처리 중)
        AnalysisJobRepository.update_status(db, analysis_job.id, "processing")

        # 이미지 로드
        image = file_handler.load_image_cv2(input_path)

        # 요청 객체 생성
        request = FaceDetectionRequest(
            min_confidence=min_confidence,
            response_format=response_format
        )

        # 얼굴 검출 실행
        faces, result_image = face_service.detect_faces(image, request)

        # 결과 이미지 저장
        result_path = file_handler.save_image_cv2(result_image, "face_detection")

        # DB에 얼굴 검출 결과 저장
        for face in faces:
            FaceResultRepository.create(
                db=db,
                analysis_job_id=analysis_job.id,
                face_id=face.face_id,
                bbox_x=face.bbox[0],
                bbox_y=face.bbox[1],
                bbox_width=face.bbox[2],
                bbox_height=face.bbox[3],
                confidence=face.confidence,
                landmarks=face.landmarks,
                result_image_path=result_path
            )

        # 실행 시간 계산
        execution_time = time.time() - start_time

        # 분석 작업 완료 처리
        AnalysisJobRepository.update_status(
            db, analysis_job.id, "completed", execution_time
        )

        # 응답 데이터 처리
        if response_format == ResponseFormat.BASE64:
            result_image_data = file_handler.image_to_base64(result_image)
        else:
            result_image_data = file_handler.get_file_url(result_path)

        return FaceDetectionResponse(
            success=True,
            message=f"{len(faces)}개의 얼굴이 검출되었습니다",
            faces=faces,
            result_image=result_image_data,
            execution_time=execution_time
        )

    except Exception as e:
        # 분석 작업 실패 처리
        if 'analysis_job' in locals():
            AnalysisJobRepository.update_status(
                db, analysis_job.id, "failed", error_message=str(e)
            )
        raise HTTPException(status_code=500, detail=f"얼굴 검출 실패: {str(e)}")

    finally:
        # 임시 파일 정리 (업로드된 원본 파일만 삭제, 결과 파일은 유지)
        file_handler.cleanup_temp_files(temp_files)

@router.get("/health")
async def face_health_check():
    """얼굴 검출 서비스 상태 확인"""
    try:
        return {
            "success": True,
            "message": "얼굴 검출 서비스가 정상 작동 중입니다",
            "service_status": "healthy",
            "detection_engine": "MediaPipe"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"얼굴 검출 서비스 오류: {str(e)}")