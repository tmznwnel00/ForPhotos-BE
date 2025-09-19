"""
Pydantic 모델 정의
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class FilterType(str, Enum):
    SEPIA = "sepia"
    GRAYSCALE = "grayscale"
    VINTAGE = "vintage"

class EmotionType(str, Enum):
    ANGER = "anger"
    CONTEMPT = "contempt"
    DISGUST = "disgust"
    FEAR = "fear"
    HAPPINESS = "happiness"
    NEUTRAL = "neutral"
    SADNESS = "sadness"
    SURPRISE = "surprise"

class ResponseFormat(str, Enum):
    BASE64 = "base64"
    URL = "url"

# 공통 응답 모델
class BaseResponse(BaseModel):
    success: bool
    message: str
    execution_time: Optional[float] = None

# 감정 분석 관련
class FaceEmotion(BaseModel):
    face_id: int
    bbox: List[float] = Field(description="[x, y, width, height]")
    emotion: EmotionType
    confidence: float = Field(ge=0.0, le=1.0)

class EmotionAnalysisRequest(BaseModel):
    conf_min: float = Field(0.0, ge=0.0, le=1.0)
    emoji_size_scale: float = Field(0.6, gt=0.0, le=2.0)
    emoji_y_offset: float = Field(0.15, ge=0.0, le=1.0)
    enable_overlap_avoid: bool = True
    response_format: ResponseFormat = ResponseFormat.URL

class EmotionAnalysisResponse(BaseResponse):
    faces: List[FaceEmotion]
    result_image: str  # base64 또는 URL
    panel_image: Optional[str] = None  # 분석 패널

# 포즈 분석 관련
class PoseType(str, Enum):
    SITTING = "sitting"
    STANDING = "standing"
    LYING = "lying"
    UNKNOWN = "unknown"

class PersonPose(BaseModel):
    person_id: int
    bbox: List[float]
    pose_type: PoseType
    confidence: float
    gender: Optional[str] = None
    keypoints: List[List[float]] = Field(description="[[x, y, confidence], ...]")

class PoseAnalysisRequest(BaseModel):
    detect_gender: bool = True
    response_format: ResponseFormat = ResponseFormat.URL

class PoseAnalysisResponse(BaseResponse):
    num_people: int
    poses: List[PersonPose]
    result_image: Optional[str] = None
    metadata: Dict[str, Any]

# 필터 적용 관련
class FilterRequest(BaseModel):
    filter_type: FilterType
    response_format: ResponseFormat = ResponseFormat.URL

class FilterResponse(BaseResponse):
    filter_applied: FilterType
    result_image: str

# 얼굴 검출 관련
class Face(BaseModel):
    face_id: int
    bbox: List[float]
    confidence: float
    landmarks: Optional[List[List[float]]] = None

class FaceDetectionRequest(BaseModel):
    min_confidence: float = Field(0.5, ge=0.0, le=1.0)
    response_format: ResponseFormat = ResponseFormat.URL

class FaceDetectionResponse(BaseResponse):
    faces: List[Face]
    result_image: Optional[str] = None

# 통합 분석 관련
class ComprehensiveAnalysisRequest(BaseModel):
    analyze_emotion: bool = True
    analyze_pose: bool = True
    detect_faces: bool = True
    apply_filter: Optional[FilterType] = None
    emotion_config: Optional[EmotionAnalysisRequest] = None
    pose_config: Optional[PoseAnalysisRequest] = None
    response_format: ResponseFormat = ResponseFormat.URL

class ComprehensiveAnalysisResponse(BaseResponse):
    emotion_analysis: Optional[EmotionAnalysisResponse] = None
    pose_analysis: Optional[PoseAnalysisResponse] = None
    face_detection: Optional[FaceDetectionResponse] = None
    filtered_image: Optional[str] = None