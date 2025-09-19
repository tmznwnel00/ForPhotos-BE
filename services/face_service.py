"""
얼굴 검출 서비스
기존 LibreFace_detect_mediapipe.py를 참고하여 구현
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple
import tempfile

import cv2
import numpy as np
import mediapipe as mp

from models.schemas import Face, FaceDetectionRequest
from core.config import settings

class FaceService:
    """얼굴 검출 서비스 - MediaPipe 사용"""

    def __init__(self):
        # MediaPipe 초기화
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_draw = mp.solutions.drawing_utils
        print("✅ FaceService initialized with MediaPipe")

    def detect_faces(
        self,
        image: np.ndarray,
        request: FaceDetectionRequest
    ) -> Tuple[List[Face], np.ndarray]:
        """
        얼굴 검출 실행

        Args:
            image: 입력 이미지 (RGB)
            request: 검출 요청 설정

        Returns:
            (faces, result_image_with_boxes)
        """
        try:
            faces = []
            result_image = image.copy()

            with self.mp_face_detection.FaceDetection(
                model_selection=0,
                min_detection_confidence=request.min_confidence
            ) as face_detection:

                # MediaPipe 추론
                results = face_detection.process(image)

                if results.detections:
                    for i, detection in enumerate(results.detections):
                        # 바운딩 박스 좌표 추출
                        bbox = self._extract_bbox_from_detection(
                            detection,
                            image.shape
                        )

                        # 랜드마크 추출 (선택적)
                        landmarks = self._extract_landmarks_from_detection(
                            detection,
                            image.shape
                        )

                        face = Face(
                            face_id=i,
                            bbox=bbox,
                            confidence=detection.score[0],
                            landmarks=landmarks
                        )
                        faces.append(face)

                        # 결과 이미지에 박스 그리기
                        result_image = self._draw_face_box(
                            result_image,
                            face
                        )

            return faces, result_image

        except Exception as e:
            print(f"❌ Face detection failed: {e}")
            return [], image.copy()

    def _extract_bbox_from_detection(
        self,
        detection,
        image_shape: tuple
    ) -> List[float]:
        """MediaPipe 검출 결과에서 바운딩 박스 추출"""
        try:
            bbox = detection.location_data.relative_bounding_box
            h, w = image_shape[:2]

            x = bbox.xmin * w
            y = bbox.ymin * h
            width = bbox.width * w
            height = bbox.height * h

            return [x, y, width, height]

        except Exception as e:
            print(f"❌ Bbox extraction failed: {e}")
            return [0, 0, 0, 0]

    def _extract_landmarks_from_detection(
        self,
        detection,
        image_shape: tuple
    ) -> List[List[float]]:
        """MediaPipe 검출 결과에서 랜드마크 추출"""
        try:
            landmarks = []
            h, w = image_shape[:2]

            # MediaPipe face detection의 key points 추출
            for keypoint in detection.location_data.relative_keypoints:
                landmarks.append([
                    keypoint.x * w,
                    keypoint.y * h,
                    1.0  # 신뢰도
                ])

            return landmarks

        except Exception as e:
            print(f"❌ Landmarks extraction failed: {e}")
            return []

    def _draw_face_box(self, image: np.ndarray, face: Face) -> np.ndarray:
        """결과 이미지에 얼굴 박스 그리기"""
        try:
            x, y, w, h = [int(coord) for coord in face.bbox]

            # 바운딩 박스 그리기
            cv2.rectangle(
                image,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),  # 초록색
                2
            )

            # 신뢰도 텍스트 추가
            confidence_text = f"Face {face.face_id}: {face.confidence:.2f}"
            cv2.putText(
                image,
                confidence_text,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            # 랜드마크 그리기 (있는 경우)
            if face.landmarks:
                for landmark in face.landmarks:
                    cv2.circle(
                        image,
                        (int(landmark[0]), int(landmark[1])),
                        3,
                        (255, 0, 0),  # 빨간색
                        -1
                    )

            return image

        except Exception as e:
            print(f"❌ Face box drawing failed: {e}")
            return image

# 전역 인스턴스
face_service = FaceService()