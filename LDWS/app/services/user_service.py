from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.core.security import hash_password
from app.db.repositories import UserRepository, StationRepository
from app.schemas.user import UserCreate, UserUpdate, UserStatusUpdate

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.station_repo = StationRepository(db)
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
        
        # Check Station tồn tại
        station = self.station_repo.get_by_id(station_id)
        if not station:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Station does not exist"
            )

        # Lưu vào db
        return self.user_repo.create(
            username=username,
            password_hash=hash_password(password),
            role=UserRole.STATION_ADMIN,
            station_id=station_id,
            is_active=True
        )
    
    # Các hàm Helper

    # Hàm tìm User
    def _get_user_or_404(self, user_id: int):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    # Hàm chỉ cho SUPER_ADMIN lấy thông tin của STATION_ADMIN
    def _get_station_admin_or_404(self, user_id: int):
        user = self._get_user_or_404(user_id)
        if user.role != UserRole.STATION_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a station_admin"
            )
        return user
    
    # Kiểm tra sự tồn tại của trạm
    def _ensure_station_exists(self, station_id: int | None):
        if station_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="station_id is required for station_admin"
            )

        station = self.station_repo.get_by_id(station_id)
        if not station:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Station does not exist"
            )
        return station
    
    # Lấy danh sách tất cả các Station_admin
    def list_station_admins(self):
        return self.user_repo.list_station_admins()
    
    # Lấy thông tin của 1 Station_admin
    def get_station_admin(self, user_id: int):
        return self._get_station_admin_or_404(user_id)
    
    # Hàm để Super_admin tạo ra Station_admin
    def create_station_admin_by_payload(self, payload: UserCreate):
        if payload.role != UserRole.STATION_ADMIN: # Không cho phép tạo ra SUPER_ADMIN
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This API only allows creating station_admin"
            )

        # Kiểm tra trùng username
        existing_user = self.user_repo.get_by_username(payload.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
    
        # Kiểm tra trạm tồn tại
        self._ensure_station_exists(payload.station_id)

        # Lưu user mới xuống DB
        return self.user_repo.create(
            username=payload.username,
            password_hash=hash_password(payload.password), 
            role=UserRole.STATION_ADMIN,
            station_id=payload.station_id,
            is_active=payload.is_active
        )

    # Cập nhật thông tin station_admin
    def update_station_admin(self, user_id: int, payload: UserUpdate):
        user = self._get_station_admin_or_404(user_id)

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return user

        # Kiểm tra trùng username
        new_username = update_data.get("username")
        if new_username and new_username != user.username:
            existing_user = self.user_repo.get_by_username(new_username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )

        # Nếu đổi trạm, kiểm tra trạm mới tồn tại
        if "station_id" in update_data:
            self._ensure_station_exists(update_data["station_id"])

        # Đổi mật khẩu
        if "password" in update_data:
            update_data["password_hash"] = hash_password(
                update_data.pop("password") # Lấy "password" ra khỏi dict, đảm bảo plain-text không bị lộ
            )
        return self.user_repo.update(user, **update_data)

    # SUPER_ADMIN để khóa / mở khóa tài khoản
    def update_station_admin_status(self, user_id: int, payload: UserStatusUpdate):
        user = self._get_station_admin_or_404(user_id)
        return self.user_repo.update(user, is_active=payload.is_active)