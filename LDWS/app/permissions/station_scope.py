from fastapi import HTTPException, status

from app.core.enums import UserRole

# Đảm bảo station_admin_1 không CRUD station_2
def ensure_station_scope(current_user, station_id: int) -> None:
    if current_user.role == UserRole.SUPER_ADMIN:
        return
    
    if current_user.role == UserRole.STATION_ADMIN and current_user.station_id == station_id:
        return
    
    # Ngoại lệ, không thuộc 2 TH thỏa mãn trên
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You cannot access resources outside your station scope"
    )

# Truy vấn dữ liệu tự động
def get_current_station_scope(current_user) -> int | None:
    if current_user.role == UserRole.STATION_ADMIN:
        return current_user.station_id # trả về id trạm
    
    return None