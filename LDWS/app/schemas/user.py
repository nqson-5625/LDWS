from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import UserRole

# Base Model
class UserBase(BaseModel):
    username: str
    role: UserRole
    station_id: int | None = None
    is_active: bool = True # Mặc định là True

# Response Model (hứng dữ liệu từ db và trả ra cho FE)
class UserResponse(UserBase):
    user_id: int
    created_at: datetime
    updated_at: datetime

    # Pydantic tự động đọc dữ liệu từ các object DB (SQLAlchemy)
    model_config = ConfigDict(from_attributes=True)

# Model tạo mới (nhận dữ liệu khi FE gửi request tạo user)
class UserCreate(BaseModel):
    username: str
    password: str
    role: UserRole
    station_id: int | None = None
    is_active: bool = True
