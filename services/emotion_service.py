"""
감정 분석 서비스
기존 emotion 모듈을 호출하여 사용
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any
import tempfile

import cv2
import numpy as np

# 기존 emotion 모듈 경로 추가
emotion_path = Path(__file__).parent.parent.parent / "emotion"
sys.path.insert(0, str(emotion_path))

from models.schemas import FaceEmotion, EmotionType, EmotionAnalysisRequest
from core.config import settings
from core.device_utils import get_device_from_env, check_device_compatibility

class EmotionService:
    """감정 분석 서비스 - 기존 emotion 모듈 호출"""

    def __init__(self):
        self.analyzer = None
        self.emoji_module = None
        self.visualize_module = None
        self.device = get_device_from_env()
        self._print_device_info()
        self._load_modules()

    def _print_device_info(self):
        """디바이스 정보 출력"""
        try:
            device_info = check_device_compatibility()
            print(f"🎭 EmotionService 초기화:")
            print(f"   - 선택된 디바이스: {self.device}")
            print(f"   - PyTorch 버전: {device_info['torch_version']}")
            print(f"   - CUDA 사용 가능: {device_info['cuda_available']}")
            if device_info['cuda_available']:
                print(f"   - GPU: {', '.join(device_info['gpu_names'])}")
        except Exception as e:
            print(f"⚠️ 디바이스 정보 출력 실패: {e}")

    def _load_modules(self):
        """기존 emotion 모듈들 로드"""
        try:
            from HSemotion.analyzer import EmotionAnalyzer
            from HSemotion.config import AppConfig
            from HSemotion import emoji
            from HSemotion import visualize

            # 설정 생성
            config = AppConfig()
            config.device = self.device  # 자동 감지된 디바이스 사용
            config.model_name = settings.EMOTION_MODEL
            config.emoji_dir = str(emotion_path / "examples" / "emojis")

            # 분석기 초기화 (명시적으로 device 전달)
            self.analyzer = EmotionAnalyzer(
                device=self.device,
                model_name=settings.EMOTION_MODEL
            )
            self.emoji_module = emoji
            self.visualize_module = visualize

            print("✅ EmotionService initialized with existing modules")

        except Exception as e:
            print(f"❌ Failed to load emotion modules: {e}")
            raise

    def analyze_emotions(
        self,
        image: np.ndarray,
        request: EmotionAnalysisRequest
    ) -> Tuple[List[FaceEmotion], np.ndarray, np.ndarray]:
        """
        기존 emotion 모듈을 사용한 감정 분석

        Args:
            image: 입력 이미지 (RGB)
            request: 분석 요청 설정

        Returns:
            (faces, result_image_with_emojis, analysis_panel)
        """
        try:
            # 1. 기존 analyzer로 감정 분석
            results = self.analyzer.analyze(
                image,
                conf_threshold=request.conf_min
            )

            # 2. 결과를 FaceEmotion 형식으로 변환
            faces = []
            for i, result in enumerate(results):
                emotion_str = result.get('emotion', 'neutral')
                emotion_type = self._str_to_emotion_type(emotion_str)

                face = FaceEmotion(
                    face_id=i,
                    bbox=result.get('bbox', [0, 0, 0, 0]),
                    emotion=emotion_type,
                    confidence=result.get('confidence', 0.0)
                )
                faces.append(face)

            # 3. 기존 emoji 모듈로 이모지 합성
            result_image = self.emoji_module.add_emotion_emojis(
                image.copy(),
                results,
                emoji_dir=str(emotion_path / "examples" / "emojis"),
                size_scale=request.emoji_size_scale,
                y_offset=request.emoji_y_offset,
                avoid_overlap=request.enable_overlap_avoid
            )

            # 4. 기존 visualize 모듈로 분석 패널 생성
            panel_image = self.visualize_module.visualize_results(
                image,
                results
            )

            return faces, result_image, panel_image

        except Exception as e:
            print(f"❌ Emotion analysis failed: {e}")
            # 실패 시 원본 이미지 반환
            return [], image.copy(), image.copy()

    def _str_to_emotion_type(self, emotion_str: str) -> EmotionType:
        """감정 문자열을 EmotionType으로 변환"""
        mapping = {
            'anger': EmotionType.ANGER,
            'contempt': EmotionType.CONTEMPT,
            'disgust': EmotionType.DISGUST,
            'fear': EmotionType.FEAR,
            'happiness': EmotionType.HAPPINESS,
            'neutral': EmotionType.NEUTRAL,
            'sadness': EmotionType.SADNESS,
            'surprise': EmotionType.SURPRISE
        }
        return mapping.get(emotion_str.lower(), EmotionType.NEUTRAL)

    def get_available_emotions(self) -> List[str]:
        """사용 가능한 감정 목록 반환"""
        return [emotion.value for emotion in EmotionType]

# 전역 인스턴스
emotion_service = EmotionService()