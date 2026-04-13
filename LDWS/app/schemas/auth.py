from pydantic import BaseModel

from app.schemas.user import UserResponse

class LoginRequest(BaseModel):
    username: str
    password: str

# Gửi Token cho client sau khi đăng nhập thành công
class TokenResponse(BaseModel):
    access_token: str # Chuỗi JWT từ hàm create_access_token() sinh ra
    token_type: str = "bearer" # mặc định

# Kiểm tra dữ liệu bên trong chuỗi JWT sau khi giải mã
class TokenPayload(BaseModel):
    sub: str
    role: str
    station_id: int | None = None
    exp: int

# Gửi thông tin cá nhân
class CurrentUserResponse(UserResponse):
    pass # class trống