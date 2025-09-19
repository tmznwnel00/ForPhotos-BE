"""
포즈 분석 API 라우터
"""

import time
import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from models.schemas import (
    PoseAnalysisRequest,
    PoseAnalysisResponse,
    ResponseFormat,
    PersonPose
)
from services.pose_service import pose_service
from utils.file_handler import file_handler
from core.database import get_db
from repositories import (
    UserRepository, ImageRepository, AnalysisJobRepository, PoseResultRepository
)
from routers.auth import get_current_active_user
from models.database import User

router = APIRouter()

@router.post("/analyze", response_model=PoseAnalysisResponse)
async def analyze_pose(
    file: UploadFile = File(...),
    detect_gender: bool = Form(True),
    response_format: ResponseFormat = Form(ResponseFormat.URL),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    포즈 분석 (사람 수 계산 + 포즈 검출 + 성별 분석)

    - **file**: 업로드할 이미지 파일
    - **Authorization**: Bearer 토큰 (헤더)
    - **detect_gender**: 성별 분석 활성화
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
            "detect_gender": detect_gender,
            "response_format": response_format
        }
        analysis_job = AnalysisJobRepository.create(
            db=db,
            image_id=db_image.id,
            job_type="pose",
            config=config
        )

        # 분석 작업 상태 업데이트 (처리 중)
        AnalysisJobRepository.update_status(db, analysis_job.id, "processing")

        # 이미지 로드
        image = file_handler.load_image_cv2(input_path)

        # 요청 객체 생성
        request = PoseAnalysisRequest(
            detect_gender=detect_gender,
            response_format=response_format
        )

        # 포즈 분석 실행 (기존 pose 모듈 호출)
        num_people, poses, metadata = pose_service.analyze_poses(image, request)

        # 결과 이미지 생성 및 저장
        result_image = image.copy()
        # TODO: 포즈 키포인트 시각화 추가
        result_path = file_handler.save_image_cv2(result_image, "pose_result")

        # DB에 포즈 분석 결과 저장
        for pose in poses:
            PoseResultRepository.create(
                db=db,
                analysis_job_id=analysis_job.id,
                person_id=pose.person_id,
                bbox_x=pose.bbox[0],
                bbox_y=pose.bbox[1],
                bbox_width=pose.bbox[2],
                bbox_height=pose.bbox[3],
                pose_type=pose.pose_type.value,
                confidence=pose.confidence,
                gender=pose.gender,
                keypoints=pose.keypoints,
                result_image_path=result_path,
                metadata=metadata
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

        return PoseAnalysisResponse(
            success=True,
            message=f"{num_people}명의 사람과 {len(poses)}개의 포즈가 검출되었습니다",
            num_people=num_people,
            poses=poses,
            result_image=result_image_data,
            metadata=metadata,
            execution_time=execution_time
        )

    except Exception as e:
        # 분석 작업 실패 처리
        if 'analysis_job' in locals():
            AnalysisJobRepository.update_status(
                db, analysis_job.id, "failed", error_message=str(e)
            )
        raise HTTPException(status_code=500, detail=f"포즈 분석 실패: {str(e)}")

    finally:
        # 임시 파일 정리 (업로드된 원본 파일만 삭제, 결과 파일은 유지)
        file_handler.cleanup_temp_files(temp_files)

@router.get("/pose-types")
async def get_available_pose_types():
    """사용 가능한 포즈 타입 목록 조회"""
    return {
        "success": True,
        "pose_types": ["sitting", "standing", "lying", "unknown"],
        "descriptions": {
            "sitting": "앉아있는 자세",
            "standing": "서있는 자세",
            "lying": "누워있는 자세",
            "unknown": "알 수 없는 자세"
        }
    }

@router.get("/health")
async def pose_health_check():
    """포즈 분석 서비스 상태 확인"""
    try:
        return {
            "success": True,
            "message": "포즈 분석 서비스가 정상 작동 중입니다",
            "service_status": "healthy",
            "features": ["pose_detection", "people_counting", "gender_analysis"]
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"포즈 분석 서비스 오류: {str(e)}")