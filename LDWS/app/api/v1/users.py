from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_super_admin
from app.db.session import get_db

from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserStatusUpdate
from app.services.user_service import UserService

router = APIRouter(
    prefix="/v1/users",
    tags=["users"],
    dependencies=[Depends(get_current_super_admin)]
)

# API lấy tất cả station_admin
@router.get("/station-admins", response_model=list[UserResponse])
def list_station_admin(
    db: Session = Depends(get_db)
):
    return UserService(db).list_station_admins()

# API lấy thông tin 1 station_admin
@router.get("/station-admins/{user_id}", response_model=UserResponse)
def get_station_admin(
    user_id: int,
    db: Session = Depends(get_db)
):
    return UserService(db).get_station_admin(user_id)

# API cho SUPER_ADMIN tạo station_admin mới
@router.post("/station-admins", response_model=UserResponse)
def create_station_admin(
    payload: UserCreate,
    db: Session = Depends(get_db)
):
    return UserService(db).create_station_admin_by_payload(payload)

# API cập nhật station_admin
@router.put("/station-admins/{user_id}", response_model=UserResponse)
def update_station_admin(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db)
):
    return UserService(db).update_station_admin(user_id, payload)

# API cập nhật trạng thái station_admin
@router.patch("/station-admins/{user_id}/status", response_model=UserResponse)
def update_station_admin_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db)
):
    return UserService(db).update_station_admin_status(user_id, payload)