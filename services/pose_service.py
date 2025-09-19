"""
포즈 분석 서비스
기존 pose 모듈을 호출하여 사용
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any
import tempfile

import cv2
import numpy as np

# 기존 pose 모듈 경로 추가
pose_path = Path(__file__).parent.parent.parent / "pose"
sys.path.insert(0, str(pose_path))

from models.schemas import PersonPose, PoseType, PoseAnalysisRequest
from core.config import settings

class PoseService:
    """포즈 분석 서비스 - 기존 pose 모듈 호출"""

    def __init__(self):
        self.pose_analysis = None
        self.main_module = None
        self.metadata_module = None
        self._load_modules()

    def _load_modules(self):
        """기존 pose 모듈들 로드"""
        try:
            import analysis
            import main
            import metadata

            self.pose_analysis = analysis
            self.main_module = main
            self.metadata_module = metadata

            print("✅ PoseService initialized with existing modules")

        except Exception as e:
            print(f"❌ Failed to load pose modules: {e}")
            raise

    def analyze_poses(
        self,
        image: np.ndarray,
        request: PoseAnalysisRequest
    ) -> Tuple[int, List[PersonPose], Dict[str, Any]]:
        """
        기존 pose 모듈을 사용한 포즈 분석

        Args:
            image: 입력 이미지 (RGB)
            request: 분석 요청 설정

        Returns:
            (num_people, poses, metadata)
        """
        try:
            # 임시 파일로 저장 (기존 모듈이 파일 경로를 요구할 수 있음)
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(tmp.name, bgr_image)
                temp_path = tmp.name

            try:
                # 1. 기존 analysis 모듈로 사람 수 계산
                num_people = self.pose_analysis.get_num_people(temp_path)

                # 2. 기존 main 모듈의 포즈 분석 함수들 사용
                poses = self._extract_poses_from_existing(image, request)

                # 3. 기존 metadata 모듈로 메타데이터 생성
                metadata_df = self.metadata_module.create_dataframe(
                    photo_ids=[0],
                    num_people_list=[num_people],
                    pose_types=[pose.pose_type.value for pose in poses] if poses else ['unknown']
                )

                metadata = {
                    'num_people': num_people,
                    'image_shape': image.shape,
                    'analysis_method': 'existing_pose_modules',
                    'dataframe': metadata_df.to_dict() if metadata_df is not None else {}
                }

                return num_people, poses, metadata

            finally:
                # 임시 파일 정리
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except Exception as e:
            print(f"❌ Pose analysis failed: {e}")
            # 실패 시 기본값 반환
            return 0, [], {'error': str(e)}

    def _extract_poses_from_existing(
        self,
        image: np.ndarray,
        request: PoseAnalysisRequest
    ) -> List[PersonPose]:
        """기존 모듈을 사용한 포즈 추출"""
        poses = []

        try:
            # MediaPipe 초기화 (기존 main.py와 동일한 방식)
            import mediapipe as mp

            mp_pose = mp.solutions.pose
            mp_draw = mp.solutions.drawing_utils

            with mp_pose.Pose(
                static_image_mode=True,
                model_complexity=2,
                enable_segmentation=False,
                min_detection_confidence=0.5
            ) as pose:

                # MediaPipe 추론
                results = pose.process(image)

                if results.pose_landmarks:
                    # 키포인트 추출
                    keypoints = []
                    for landmark in results.pose_landmarks.landmark:
                        keypoints.append([
                            landmark.x * image.shape[1],
                            landmark.y * image.shape[0],
                            landmark.visibility
                        ])

                    # 기존 analysis 모듈로 포즈 타입 분류
                    keypoint_array = np.array(keypoints)
                    pose_type_str = self.pose_analysis.get_pose_type_from_array(keypoint_array)
                    pose_type = self._str_to_pose_type(pose_type_str)

                    # 성별 분석 (요청 시)
                    gender = None
                    if request.detect_gender:
                        gender = self._analyze_gender_with_existing(image)

                    # 바운딩 박스 계산
                    bbox = self._calculate_bbox_from_keypoints(keypoints)

                    pose_data = PersonPose(
                        person_id=0,
                        bbox=bbox,
                        pose_type=pose_type,
                        confidence=0.8,
                        gender=gender,
                        keypoints=keypoints
                    )

                    poses.append(pose_data)

        except Exception as e:
            print(f"❌ Pose extraction failed: {e}")

        return poses

    def _analyze_gender_with_existing(self, image: np.ndarray) -> str:
        """기존 main.py의 성별 분석 로직 사용"""
        try:
            # 기존 main.py에서 사용하는 방식과 동일
            from deepface import DeepFace

            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(tmp.name, bgr_image)

                try:
                    result = DeepFace.analyze(
                        tmp.name,
                        actions=['gender'],
                        enforce_detection=False
                    )

                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get('dominant_gender', 'unknown')
                    else:
                        return result.get('dominant_gender', 'unknown')

                finally:
                    os.unlink(tmp.name)

        except Exception as e:
            print(f"❌ Gender analysis failed: {e}")
            return 'unknown'

    def _str_to_pose_type(self, pose_str: str) -> PoseType:
        """포즈 문자열을 PoseType으로 변환"""
        mapping = {
            'sitting': PoseType.SITTING,
            'standing': PoseType.STANDING,
            'lying': PoseType.LYING
        }
        return mapping.get(pose_str.lower(), PoseType.UNKNOWN)

    def _calculate_bbox_from_keypoints(self, keypoints: List[List[float]]) -> List[float]:
        """키포인트로부터 바운딩 박스 계산"""
        try:
            if not keypoints:
                return [0, 0, 0, 0]

            # 유효한 키포인트만 필터링
            valid_points = [kp for kp in keypoints if kp[2] > 0.5]

            if not valid_points:
                return [0, 0, 0, 0]

            x_coords = [kp[0] for kp in valid_points]
            y_coords = [kp[1] for kp in valid_points]

            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)

            return [x_min, y_min, x_max - x_min, y_max - y_min]

        except Exception as e:
            print(f"❌ Bbox calculation failed: {e}")
            return [0, 0, 0, 0]

# 전역 인스턴스
pose_service = PoseService()