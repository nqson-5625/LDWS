from fastapi import APIRouter, Depends

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.schemas.auth import TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

# Tạo nhóm Router xác thực
router = APIRouter(prefix="/v1/auth", tags=["auth"])

# API đăng nhập và lấy Token
# POST /api/v1/auth/login
@router.post("/login", response_model=TokenResponse)
def login(
    # OAuth2PasswordRequestForm bắt client gửi dạng Form Data (username và password)
    form_data: OAuth2PasswordRequestForm = Depends(),
    # Xin cấp kết nối đến db
    db: Session = Depends(get_db)
):
    return AuthService(db).login(form_data.username, form_data.password)

# API lấy thông tin cá nhân
# GET /api/v1/auth/me
@router.get("/me", response_model=UserResponse)
def get_me(
    # Lấy current_user có Token hợp lệ
    current_user = Depends(get_current_active_user)
):
    return current_user