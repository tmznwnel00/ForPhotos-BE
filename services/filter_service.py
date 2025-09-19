"""
필터 효과 서비스
기존 simple_filter.py를 참고하여 구현
"""

import cv2
import numpy as np
from typing import Dict, Callable

from models.schemas import FilterType

class FilterService:
    """이미지 필터 서비스"""

    def __init__(self):
        self.filters: Dict[FilterType, Callable] = {
            FilterType.SEPIA: self._apply_sepia,
            FilterType.GRAYSCALE: self._apply_grayscale,
            FilterType.VINTAGE: self._apply_vintage
        }
        print("✅ FilterService initialized")

    def apply_filter(self, image: np.ndarray, filter_type: FilterType) -> np.ndarray:
        """
        이미지에 필터 적용

        Args:
            image: 입력 이미지 (RGB)
            filter_type: 적용할 필터 타입

        Returns:
            필터 적용된 이미지 (RGB)
        """
        if filter_type not in self.filters:
            raise ValueError(f"지원하지 않는 필터: {filter_type}")

        try:
            return self.filters[filter_type](image)
        except Exception as e:
            print(f"❌ Filter application failed: {e}")
            raise

    def _apply_sepia(self, img: np.ndarray) -> np.ndarray:
        """세피아 필터 적용"""
        sepia_filter = np.array([
            [0.272, 0.534, 0.131],
            [0.349, 0.686, 0.168],
            [0.393, 0.769, 0.189]
        ])
        return cv2.transform(img, sepia_filter)

    def _apply_grayscale(self, img: np.ndarray) -> np.ndarray:
        """그레이스케일 필터 적용"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            # 3채널로 다시 변환
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        else:
            return img

    def _apply_vintage(self, img: np.ndarray) -> np.ndarray:
        """빈티지 필터 적용"""
        # RGB -> HSV 변환
        img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

        # HSV 조정
        img_hsv[:, :, 1] = img_hsv[:, :, 1] * 0.3  # 채도 감소
        img_hsv[:, :, 2] = img_hsv[:, :, 2] * 0.8  # 명도 감소
        img_hsv[:, :, 0] = np.clip(img_hsv[:, :, 0] * 1.1, 0, 179)  # 색조 조정

        # HSV -> RGB 변환
        img_vintage = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2RGB)

        # 세피아 효과 추가
        sepia_filter = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131]
        ])
        img_vintage = cv2.transform(img_vintage, sepia_filter)

        # 대비 및 밝기 조정
        img_vintage = cv2.convertScaleAbs(img_vintage, alpha=0.9, beta=10)

        return img_vintage

    def get_available_filters(self) -> list:
        """사용 가능한 필터 목록 반환"""
        return [filter_type.value for filter_type in FilterType]

# 전역 인스턴스
filter_service = FilterService()