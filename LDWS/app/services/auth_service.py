from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.core.security import create_access_token, decode_token, verify_password
from app.db.repositories import UserRepository

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db) # Khởi tạo kho lưu trữ db

    # Xác thực thông tin đăng nhập
    def authenticate_user(self, username: str, password: str):
        user = self.user_repo.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"}             
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive",
            )
        
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Station_admin nhưng ID trạm là None
        if user.role == UserRole.STATION_ADMIN and user.station_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Station admin account is not assigned to any station"
            )
        
        return user
    
    # Thực hiện đăng nhập và sinh Token
    def login(self, username: str, password: str) -> dict:
        # Kiểm tra thông tin đăng nhập
        user = self.authenticate_user(username, password)

        # Sinh JWT Token
        access_token = create_access_token(
            subject=user.username,
            extra_claims={
                "role": user.role,
                "station_id": user.station_id,
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    # Xác thực người dùng thông qua Token
    def get_current_user_from_token(self, token: str):
        payload = decode_token(token)
        username = payload.get("sub")

        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid adthentication token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user = self.user_repo.get_by_username(username)
        # Token chưa hết hạn nhưng user bị xóa 
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive"
            )
        
        return user