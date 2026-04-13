from fastapi import HTTPException, status

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.core.security import hash_password
from app.db.models.user import User
from app.db.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    # Tạo super admin
    def create_super_admin(self, username: str, password: str):
        existing_user = self.user_repo.get_by_username(username)

        # Nếu username đã tồn tại
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Lưu vào db
        return self.user_repo.create(
            username=username,
            password_hash=hash_password(password),
            role=UserRole.SUPER_ADMIN,
            station_id=None,
            is_active=True
        )
    
    # Tạo station admin
    def create_station_admin(self, username: str, password: str, station_id: int):
        existing_user = self.user_repo.get_by_username(username)

        # Nếu username đã tồn tại
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Lưu vào db
        return self.user_repo.create(
            username=username,
            password_hash=hash_password(password),
            role=UserRole.STATION_ADMIN,
            station_id=station_id,
            is_active=True
        )
    