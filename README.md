# ForPhotos-ML Backend API

## 📋 개요

ForPhotos-ML 프로젝트의 백엔드 API 서버입니다. 기존에 구현된 ML 모듈들을 통합하여 RESTful API로 제공합니다.

## 🚀 주요 기능

### 1. 감정 분석 API (`/api/emotion`)
- **얼굴 검출** + **감정 분류** + **이모지 합성** 통합 파이프라인
- 기존 `emotion/HSemotion` 모듈 활용
- 8가지 감정 분류: anger, contempt, disgust, fear, happiness, neutral, sadness, surprise

### 2. 포즈 분석 API (`/api/pose`)
- **사람 수 계산** + **포즈 검출** + **성별 분석**
- 기존 `pose/` 모듈 활용 (MediaPipe + YOLO)
- 포즈 타입: sitting, standing, lying

### 3. 필터 효과 API (`/api/filter`)
- 이미지 필터 적용
- 기존 `simple_filter.py` 기능 활용
- 필터 타입: sepia, grayscale, vintage

### 4. 얼굴 검출 API (`/api/face`)
- 순수 얼굴 검출 기능
- MediaPipe 기반 구현

## 📁 프로젝트 구조

```
backend/
├── main.py                 # FastAPI 애플리케이션 진입점
├── requirements.txt        # 의존성 패키지
├── core/
│   ├── __init__.py
│   └── config.py          # 애플리케이션 설정
├── models/
│   ├── __init__.py
│   └── schemas.py         # Pydantic 모델 정의
├── services/              # 비즈니스 로직
│   ├── __init__.py
│   ├── emotion_service.py # 감정 분석 서비스
│   ├── pose_service.py    # 포즈 분석 서비스
│   ├── filter_service.py  # 필터 효과 서비스
│   └── face_service.py    # 얼굴 검출 서비스
├── routers/               # API 라우터
│   ├── __init__.py
│   ├── emotion.py         # 감정 분석 API
│   ├── pose.py           # 포즈 분석 API
│   ├── filter.py         # 필터 효과 API
│   └── face.py           # 얼굴 검출 API
├── utils/
│   ├── __init__.py
│   └── file_handler.py   # 파일 처리 유틸리티
└── storage/              # 파일 저장소
    ├── uploads/          # 업로드된 파일
    └── outputs/          # 처리 결과 파일
```

## 🔧 설치 및 실행

### 1. 환경 설정

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 서버 실행

```bash
python main.py
```

또는

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. API 문서 확인

서버 실행 후 브라우저에서 접속:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📖 API 사용 예제

### 감정 분석 API

```bash
curl -X POST "http://localhost:8000/api/emotion/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@photo.jpg" \
  -F "conf_min=0.5" \
  -F "emoji_size_scale=0.6" \
  -F "response_format=url"
```

### 포즈 분석 API

```bash
curl -X POST "http://localhost:8000/api/pose/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@photo.jpg" \
  -F "detect_gender=true" \
  -F "response_format=url"
```

### 필터 효과 API

```bash
curl -X POST "http://localhost:8000/api/filter/apply" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@photo.jpg" \
  -F "filter_type=sepia" \
  -F "response_format=url"
```

### 얼굴 검출 API

```bash
curl -X POST "http://localhost:8000/api/face/detect" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@photo.jpg" \
  -F "min_confidence=0.5" \
  -F "response_format=url"
```

## ⚙️ 설정

`core/config.py`에서 다음 설정들을 변경할 수 있습니다:

```python
# 서버 설정
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# 파일 설정
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp"]

# AI 모델 설정
EMOTION_DEVICE = "cpu"  # or "cuda"
EMOTION_MODEL = "enet_b2_8"
```

## 📦 응답 형식

### 1. URL 방식 (기본)
```json
{
  "success": true,
  "message": "처리 완료",
  "result_image": "/files/abc123_result.jpg",
  "execution_time": 2.3
}
```

### 2. Base64 방식
```json
{
  "success": true,
  "message": "처리 완료",
  "result_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABA...",
  "execution_time": 2.3
}
```

## 🔗 기존 모듈과의 연동

이 백엔드는 기존 ML 모듈들을 **수정하지 않고** 그대로 활용합니다:

- `../emotion/HSemotion/` → 감정 분석
- `../pose/` → 포즈 분석
- `../simple_filter.py` → 필터 효과
- `../LibreFace_detect_mediapipe.py` → 얼굴 검출 (참고)

## 🛠️ 트러블슈팅

### 모듈 import 오류
```bash
# Python path에 상위 디렉토리 추가
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."
```

### GPU 사용 설정
```python
# core/config.py
EMOTION_DEVICE = "cuda"  # GPU 사용
```

### 포트 변경
```python
# core/config.py
PORT = 8080  # 다른 포트 사용
```

## 📋 상태 확인 엔드포인트

- `/health` - 전체 서버 상태
- `/api/emotion/health` - 감정 분석 서비스 상태
- `/api/pose/health` - 포즈 분석 서비스 상태
- `/api/face/health` - 얼굴 검출 서비스 상태

---

## 🚀 프로덕션 배포

```bash
# 프로덕션 실행
uvicorn main:app --host 0.0.0.0 --port 8000

# Docker 사용 (선택사항)
# Dockerfile 생성 후
docker build -t forphotos-ml-backend .
docker run -p 8000:8000 forphotos-ml-backend
```