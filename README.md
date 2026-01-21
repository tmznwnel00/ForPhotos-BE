# ForPhotos-ML: The Vibe-Coded Backend

<div align="center">

![Vibe Coding](https://img.shields.io/badge/Vibe%20Coding-100%25-7000FF?style=for-the-badge&logo=openai&logoColor=white)
![No Code](https://img.shields.io/badge/Code_Written_By-AI-000000?style=for-the-badge&logo=robotframework&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688?style=for-the-badge&logo=fastapi&logoColor=white)

**"Designed by Human, Coded by AI."**

</div>

---

## 프로젝트 정체성: What is VIBECODE?

이 프로젝트는 전통적인 코딩 방식(Syntax-driven)을 따르지 않았습니다.
오직 자연어 프롬프트와 아키텍처 설계(Logic-driven)만으로 완성된 100% NOCODE / VIBECODE 결과물입니다.

개발자는 "무엇을 만들고 싶은지(Vibe)"를 정의했고, AI는 그 의도를 완벽한 FastAPI 백엔드 코드로 구현했습니다. 복잡한 ML 모듈 통합부터 에러 핸들링, 파일 구조화까지 모든 라인(Line of Code)은 AI와의 대화를 통해 탄생했습니다.

###  Role Definition
* **Director (Human)**: 아키텍처 설계, 모듈 선정, 비즈니스 로직 정의, "Vibe" 전달
* **Developer (AI Agent)**: Python 코딩, 디버깅, 리팩토링, 문서화

---

## 개요

ForPhotos-ML 프로젝트의 백엔드 API 서버입니다. 기존에 파편화되어 있던 ML 모듈(감정 분석, 포즈 인식 등)들을 AI가 분석하여 하나의 통합된 **RESTful API**로 재구축했습니다.

## 주요 기능 (Powered by AI Integration)

AI가 기존 레거시 코드들을 분석하여 다음과 같은 API로 변환했습니다:

### 1. 감정 분석 API (`/api/emotion`)
- **기능**: 얼굴 검출 → 감정 분류 → 이모지 합성 파이프라인 자동화
- **Source**: `emotion/HSemotion` 모듈 랩핑
- **분류**: 8가지 감정 (anger, happiness, neutral, sadness 등)

### 2. 포즈 분석 API (`/api/pose`)
- **기능**: MediaPipe + YOLO 기반의 사람 수 계산 및 포즈/성별 분석
- **Source**: `pose/` 모듈 통합
- **분류**: sitting, standing, lying

### 3. 필터 효과 API (`/api/filter`)
- **기능**: 이미지 필터링 프로세스 API화
- **Source**: `simple_filter.py` 활용
- **타입**: sepia, grayscale, vintage

### 4. 얼굴 검출 API (`/api/face`)
- **기능**: 순수 얼굴 영역 좌표 추출
- **Engine**: MediaPipe 기반

---

## AI가 설계한 프로젝트 구조

AI에게 "확장성 있고 유지보수 용이한 FastAPI 구조"를 요청했을 때 출력된 아키텍처입니다.

```bash
backend/
├── main.py                 # FastAPI 진입점
├── core/                   # 설정 관리 (Config)
├── models/                 # Pydantic 데이터 스키마
├── services/               # 비즈니스 로직 (ML 모듈 연동)
├── routers/                # API 라우팅 계층
├── utils/                  # 파일 처리 유틸리티
└── storage/                # 파일 입출력 저장소
