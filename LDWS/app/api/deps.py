from typing import Annotated # Đính kèm thêm thông tin và khai báo kiểu dữ liệu

from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.core.security import oauth2_scheme
from app.db.session import get_db
from app.permissions.authz import require_roles
from app.services.auth_service import AuthService

DBSessionDep = Annotated[Session, Depends(get_db)]


# Lấy thông tin user hiện tại
def get_current_user(
    db: DBSessionDep, # Tự động xin FastAPI 1 kết nối DB
    token: Annotated[str, Depends(oauth2_scheme)] # Tự động xin FastAPI chuỗi Token từ Header
):
    return AuthService(db).get_current_user_from_token(token)

# Lấy user đang hoạt động
def get_current_active_user(
    # Bắt buộc chạy get_current_user() trước, lấy kết quả trả về cho current_user
    current_user=Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

def get_current_super_admin(
    current_user=Depends(get_current_user)
):
    # Kiểm tra xem có phải SUPER_ADMIN không
    return require_roles(UserRole.SUPER_ADMIN)(current_user)

def get_current_station_admin(
    current_user=Depends(get_current_user)
):
    return require_roles(UserRole.STATION_ADMIN)(current_user)