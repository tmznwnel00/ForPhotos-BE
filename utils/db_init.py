"""
데이터베이스 초기화 유틸리티
"""

import os
from core.database import create_tables, engine
from core.config import settings

def init_database():
    """데이터베이스 및 필요한 디렉토리 초기화"""

    # storage 디렉토리 생성
    os.makedirs("./storage", exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

    # 데이터베이스 테이블 생성
    print("📊 Initializing database...")
    create_tables()
    print("✅ Database tables created successfully")

    return True

def reset_database():
    """데이터베이스 초기화 (모든 데이터 삭제)"""
    from models.database import Base

    print("⚠️  Resetting database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Database reset completed")

def migrate_database():
    """데이터베이스 스키마 마이그레이션 (기존 데이터 유지)"""
    from models.database import Base

    print("🔄 Migrating database schema...")
    # 새로운 컬럼 추가를 위해 테이블 재생성
    # 실제 프로덕션에서는 Alembic 사용 권장
    Base.metadata.create_all(bind=engine)
    print("✅ Database migration completed")

if __name__ == "__main__":
    init_database()