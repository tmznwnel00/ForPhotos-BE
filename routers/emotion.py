"""
감정 분석 API 라우터
"""

import time
import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from models.schemas import (
    EmotionAnalysisRequest,
    EmotionAnalysisResponse,
    ResponseFormat,
    FaceEmotion
)
from services.emotion_service import emotion_service
from utils.file_handler import file_handler
from core.database import get_db
from repositories import (
    UserRepository, ImageRepository, AnalysisJobRepository, EmotionResultRepository
)
from routers.auth import get_current_active_user
from models.database import User

router = APIRouter()

@router.post("/analyze", response_model=EmotionAnalysisResponse)
async def analyze_emotion(
    file: UploadFile = File(...),
    conf_min: float = Form(0.0),
    emoji_size_scale: float = Form(0.6),
    emoji_y_offset: float = Form(0.15),
    enable_overlap_avoid: bool = Form(True),
    response_format: ResponseFormat = Form(ResponseFormat.URL),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    감정 분석 (얼굴 검출 + 감정 분류 + 이모지 합성)

    - **file**: 업로드할 이미지 파일
    - **Authorization**: Bearer 토큰 (헤더)
    - **conf_min**: 감정 신뢰도 임계값 (0.0-1.0)
    - **emoji_size_scale**: 얼굴 대비 이모지 크기 비율
    - **emoji_y_offset**: 얼굴 위쪽 오프셋 비율
    - **enable_overlap_avoid**: 이모지 겹침 방지 활성화
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
            "conf_min": conf_min,
            "emoji_size_scale": emoji_size_scale,
            "emoji_y_offset": emoji_y_offset,
            "enable_overlap_avoid": enable_overlap_avoid,
            "response_format": response_format
        }
        analysis_job = AnalysisJobRepository.create(
            db=db,
            image_id=db_image.id,
            job_type="emotion",
            config=config
        )

        # 분석 작업 상태 업데이트 (처리 중)
        AnalysisJobRepository.update_status(db, analysis_job.id, "processing")

        # 이미지 로드
        image = file_handler.load_image_cv2(input_path)

        # 요청 객체 생성
        request = EmotionAnalysisRequest(
            conf_min=conf_min,
            emoji_size_scale=emoji_size_scale,
            emoji_y_offset=emoji_y_offset,
            enable_overlap_avoid=enable_overlap_avoid,
            response_format=response_format
        )

        # 감정 분석 실행 (기존 emotion 모듈 호출)
        faces, result_image, panel_image = emotion_service.analyze_emotions(image, request)

        # 결과 이미지 처리 및 저장
        result_path = file_handler.save_image_cv2(result_image, "emotion_result")
        panel_path = file_handler.save_image_cv2(panel_image, "emotion_panel")

        # DB에 감정 분석 결과 저장
        for face in faces:
            EmotionResultRepository.create(
                db=db,
                analysis_job_id=analysis_job.id,
                face_id=face.face_id,
                bbox_x=face.bbox[0],
                bbox_y=face.bbox[1],
                bbox_width=face.bbox[2],
                bbox_height=face.bbox[3],
                emotion=face.emotion.value,
                confidence=face.confidence,
                result_image_path=result_path,
                panel_image_path=panel_path
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
            panel_image_data = file_handler.image_to_base64(panel_image)
        else:
            result_image_data = file_handler.get_file_url(result_path)
            panel_image_data = file_handler.get_file_url(panel_path)

        return EmotionAnalysisResponse(
            success=True,
            message=f"{len(faces)}개의 얼굴에서 감정 분석이 완료되었습니다",
            faces=faces,
            result_image=result_image_data,
            panel_image=panel_image_data,
            execution_time=execution_time
        )

    except Exception as e:
        # 분석 작업 실패 처리
        if 'analysis_job' in locals():
            AnalysisJobRepository.update_status(
                db, analysis_job.id, "failed", error_message=str(e)
            )
        raise HTTPException(status_code=500, detail=f"감정 분석 실패: {str(e)}")

    finally:
        # 임시 파일 정리 (업로드된 원본 파일만 삭제, 결과 파일은 유지)
        file_handler.cleanup_temp_files(temp_files)

@router.get("/emotions")
async def get_available_emotions():
    """사용 가능한 감정 목록 조회"""
    return {
        "success": True,
        "emotions": emotion_service.get_available_emotions(),
        "descriptions": {
            "anger": "분노",
            "contempt": "경멸",
            "disgust": "혐오",
            "fear": "공포",
            "happiness": "행복",
            "neutral": "중성",
            "sadness": "슬픔",
            "surprise": "놀람"
        }
    }

@router.get("/health")
async def emotion_health_check():
    """감정 분석 서비스 상태 확인"""
    try:
        # 서비스가 정상적으로 초기화되었는지 확인
        emotions = emotion_service.get_available_emotions()
        return {
            "success": True,
            "message": "감정 분석 서비스가 정상 작동 중입니다",
            "available_emotions": len(emotions),
            "service_status": "healthy"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"감정 분석 서비스 오류: {str(e)}")