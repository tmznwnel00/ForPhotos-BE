"""
파일 처리 유틸리티
"""

import os
import uuid
import base64
import aiofiles
from io import BytesIO
from typing import Optional, Tuple
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from fastapi import UploadFile, HTTPException

from core.config import settings

class FileHandler:
    """파일 업로드/다운로드/변환 처리"""

    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.output_dir = Path(settings.OUTPUT_DIR)

        # 디렉토리 생성
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def validate_file(self, file: UploadFile) -> None:
        """파일 유효성 검증"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="파일명이 없습니다")

        # 확장자 확인
        ext = Path(file.filename).suffix.lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 파일 형식입니다. 허용: {settings.ALLOWED_EXTENSIONS}"
            )

    async def save_upload_file(self, file: UploadFile) -> str:
        """업로드된 파일 저장"""
        self.validate_file(file)

        # 고유 파일명 생성
        file_id = str(uuid.uuid4())
        ext = Path(file.filename).suffix.lower()
        saved_path = self.upload_dir / f"{file_id}{ext}"

        # 파일 저장
        async with aiofiles.open(saved_path, 'wb') as f:
            content = await file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(status_code=413, detail="파일 크기가 너무 큽니다")
            await f.write(content)

        return str(saved_path)

    def load_image_cv2(self, file_path: str) -> np.ndarray:
        """이미지를 OpenCV 형식으로 로드"""
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")

        image = cv2.imread(file_path)
        if image is None:
            raise HTTPException(status_code=400, detail="이미지를 읽을 수 없습니다")

        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def load_image_pil(self, file_path: str) -> Image.Image:
        """이미지를 PIL 형식으로 로드"""
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")

        try:
            return Image.open(file_path).convert('RGB')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"이미지 로드 실패: {str(e)}")

    def save_image_cv2(self, image: np.ndarray, suffix: str = "result") -> str:
        """OpenCV 이미지 저장"""
        file_id = str(uuid.uuid4())
        output_path = self.output_dir / f"{file_id}_{suffix}.jpg"

        # RGB -> BGR 변환 후 저장
        bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(output_path), bgr_image)

        return str(output_path)

    def save_image_pil(self, image: Image.Image, suffix: str = "result") -> str:
        """PIL 이미지 저장"""
        file_id = str(uuid.uuid4())
        output_path = self.output_dir / f"{file_id}_{suffix}.jpg"

        image.save(output_path, "JPEG", quality=95)
        return str(output_path)

    def image_to_base64(self, image: np.ndarray) -> str:
        """이미지를 base64로 변환"""
        # RGB -> BGR 변환
        bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # 이미지 인코딩
        _, buffer = cv2.imencode('.jpg', bgr_image)
        base64_str = base64.b64encode(buffer).decode('utf-8')

        return f"data:image/jpeg;base64,{base64_str}"

    def file_to_base64(self, file_path: str) -> str:
        """파일을 base64로 변환"""
        with open(file_path, 'rb') as f:
            base64_str = base64.b64encode(f.read()).decode('utf-8')

        return f"data:image/jpeg;base64,{base64_str}"

    def get_file_url(self, file_path: str) -> str:
        """파일의 접근 가능한 URL 반환"""
        # 실제 환경에서는 정적 파일 서빙 URL로 변경
        return f"/files/{Path(file_path).name}"

    def cleanup_temp_files(self, file_paths: list) -> None:
        """임시 파일들 정리"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"파일 삭제 실패 {file_path}: {e}")

# 전역 인스턴스
file_handler = FileHandler()