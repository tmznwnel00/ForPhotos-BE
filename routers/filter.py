"""
필터 효과 API 라우터
"""

import time
import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from models.schemas import FilterType, FilterRequest, FilterResponse, ResponseFormat
from services.filter_service import filter_service
from utils.file_handler import file_handler
from core.database import get_db
from repositories import (
    UserRepository, ImageRepository, AnalysisJobRepository, FilterResultRepository
)
from routers.auth import get_current_active_user
from models.database import User

router = APIRouter()

@router.post("/apply", response_model=FilterResponse)
async def apply_filter(
    file: UploadFile = File(...),
    filter_type: FilterType = Form(...),
    response_format: ResponseFormat = Form(ResponseFormat.URL),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    이미지에 필터 효과 적용

    - **file**: 업로드할 이미지 파일
    - **Authorization**: Bearer 토큰 (헤더)
    - **filter_type**: 적용할 필터 (sepia, grayscale, vintage)
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
            "filter_type": filter_type,
            "response_format": response_format
        }
        analysis_job = AnalysisJobRepository.create(
            db=db,
            image_id=db_image.id,
            job_type="filter",
            config=config
        )

        # 분석 작업 상태 업데이트 (처리 중)
        AnalysisJobRepository.update_status(db, analysis_job.id, "processing")

        # 이미지 로드
        image = file_handler.load_image_cv2(input_path)

        # 필터 적용
        filtered_image = filter_service.apply_filter(image, filter_type)

        # 결과 이미지 저장
        output_path = file_handler.save_image_cv2(
            filtered_image,
            f"filtered_{filter_type.value}"
        )

        # DB에 필터 적용 결과 저장
        FilterResultRepository.create(
            db=db,
            analysis_job_id=analysis_job.id,
            filter_type=filter_type.value,
            result_image_path=output_path
        )

        # 실행 시간 계산
        execution_time = time.time() - start_time

        # 분석 작업 완료 처리
        AnalysisJobRepository.update_status(
            db, analysis_job.id, "completed", execution_time
        )

        # 응답 데이터 처리
        if response_format == ResponseFormat.BASE64:
            result_image = file_handler.image_to_base64(filtered_image)
        else:
            result_image = file_handler.get_file_url(output_path)

        return FilterResponse(
            success=True,
            message=f"{filter_type.value} 필터가 성공적으로 적용되었습니다",
            filter_applied=filter_type,
            result_image=result_image,
            execution_time=execution_time
        )

    except Exception as e:
        # 분석 작업 실패 처리
        if 'analysis_job' in locals():
            AnalysisJobRepository.update_status(
                db, analysis_job.id, "failed", error_message=str(e)
            )
        raise HTTPException(status_code=500, detail=f"필터 적용 실패: {str(e)}")

    finally:
        # 임시 파일 정리 (업로드된 원본 파일만 삭제, 결과 파일은 유지)
        file_handler.cleanup_temp_files(temp_files)

@router.get("/types")
async def get_filter_types():
    """사용 가능한 필터 타입 목록 조회"""
    return {
        "success": True,
        "filters": filter_service.get_available_filters(),
        "descriptions": {
            "sepia": "세피아 톤 효과",
            "grayscale": "흑백 변환",
            "vintage": "빈티지 스타일 효과"
        }
    }