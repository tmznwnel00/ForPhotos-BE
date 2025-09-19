"""
사용자 관리 API 라우터
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.database import get_db
from repositories import UserRepository, ImageRepository

router = APIRouter()

# Pydantic 모델들
class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: str

    class Config:
        from_attributes = True

class UserStats(BaseModel):
    user_id: int
    username: str
    total_images: int
    total_analyses: int

@router.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """새 사용자 생성"""
    # 중복 확인
    existing_user = UserRepository.get_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자명입니다")

    existing_email = UserRepository.get_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다")

    # 사용자 생성
    user = UserRepository.create(db, user_data.username, user_data.email)
    return user

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """사용자 정보 조회"""
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return user

@router.get("/users", response_model=List[UserResponse])
async def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """사용자 목록 조회"""
    users = UserRepository.get_all(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}/stats", response_model=UserStats)
async def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    """사용자 통계 조회"""
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    total_images = ImageRepository.count_by_user(db, user_id)

    # 분석 개수는 나중에 추가 (현재는 0으로 설정)
    total_analyses = 0

    return UserStats(
        user_id=user.id,
        username=user.username,
        total_images=total_images,
        total_analyses=total_analyses
    )

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """사용자 정보 수정"""
    # 기존 사용자 확인
    existing_user = UserRepository.get_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    # 사용자명 중복 확인 (자신 제외)
    username_check = UserRepository.get_by_username(db, user_data.username)
    if username_check and username_check.id != user_id:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자명입니다")

    # 이메일 중복 확인 (자신 제외)
    email_check = UserRepository.get_by_email(db, user_data.email)
    if email_check and email_check.id != user_id:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다")

    # 사용자 정보 업데이트
    updated_user = UserRepository.update(
        db, user_id,
        username=user_data.username,
        email=user_data.email
    )
    return updated_user

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """사용자 삭제"""
    success = UserRepository.delete(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    return {"message": "사용자가 성공적으로 삭제되었습니다"}