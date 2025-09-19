"""
Image 모델 CRUD 작업
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from models.database import Image

class ImageRepository:
    """Image 테이블 CRUD 작업"""

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        filename: str,
        original_filename: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> Image:
        """새 이미지 레코드 생성"""
        db_image = Image(
            user_id=user_id,
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            width=width,
            height=height
        )
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        return db_image

    @staticmethod
    def get_by_id(db: Session, image_id: int) -> Optional[Image]:
        """ID로 이미지 조회"""
        return db.query(Image).filter(Image.id == image_id).first()

    @staticmethod
    def get_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Image]:
        """사용자별 이미지 목록 조회"""
        return db.query(Image)\
            .filter(Image.user_id == user_id)\
            .offset(skip).limit(limit)\
            .order_by(Image.uploaded_at.desc())\
            .all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Image]:
        """모든 이미지 조회 (페이징)"""
        return db.query(Image)\
            .offset(skip).limit(limit)\
            .order_by(Image.uploaded_at.desc())\
            .all()

    @staticmethod
    def delete(db: Session, image_id: int) -> bool:
        """이미지 삭제"""
        db_image = ImageRepository.get_by_id(db, image_id)
        if not db_image:
            return False

        db.delete(db_image)
        db.commit()
        return True

    @staticmethod
    def count_by_user(db: Session, user_id: int) -> int:
        """사용자별 이미지 개수"""
        return db.query(Image).filter(Image.user_id == user_id).count()