"""
User 모델 CRUD 작업
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from models.database import User
from datetime import datetime

class UserRepository:
    """User 테이블 CRUD 작업"""

    @staticmethod
    def create(db: Session, username: str, email: str, hashed_password: str) -> User:
        """새 사용자 생성"""
        db_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """ID로 사용자 조회"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """사용자명으로 사용자 조회"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """모든 사용자 조회 (페이징)"""
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, user_id: int, **kwargs) -> Optional[User]:
        """사용자 정보 수정"""
        db_user = UserRepository.get_by_id(db, user_id)
        if not db_user:
            return None

        for key, value in kwargs.items():
            if hasattr(db_user, key):
                setattr(db_user, key, value)

        db_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        """사용자 삭제"""
        db_user = UserRepository.get_by_id(db, user_id)
        if not db_user:
            return False

        db.delete(db_user)
        db.commit()
        return True