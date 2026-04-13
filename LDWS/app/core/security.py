from datetime import datetime, timedelta, timezone
from typing import Any # Any chỉ định 1 biến có thể là bất kỳ kiểu dữ liệu nào

import jwt # encode & decode chuỗi JSON Web Token
from fastapi import HTTPException, status #HTTPException (để ném lỗi HTTP) và status (chứa các mã lỗi HTTP như 401, 404...)
from fastapi.security import OAuth2PasswordBearer # API dùng chuẩn OAuth2
from passlib.context import CryptContext # Xử lý việc hash password an toàn

from app.core.config import settings

pwd_context = CryptContext(
    schemes=["bcrypt"], # thuật toán bcrypt xử lý mật khẩu
    deprecated="auto"   # đánh dấu các chuỗi băm cũ không dùng nữa nếu đổi thuật toán
)

# Swagger dùng endpoint để lấy token login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Đăng ký tài khoản hoặc đổi mật khẩu
def hash_password(password: str) -> str:
    return pwd_context.hash(password) # plain text -> cipher text không thể dịch ngược

# Xác minh mật khẩu
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password) # Xác thực pass vừa nhập và hashpass trong db

# Tạo JWT Access Token sau khi đăng nhập thành công
def create_access_token(
    subject: str, # Email/ID của user để định danh token này của ai
    expire_minutes: int | None = None, # Số phút token sẽ sống
    extra_claims: dict[str, Any] | None = None # Thông tin phụ muốn đính kèm
) -> str:
    expire_minutes = expire_minutes or settings.jwt_access_token_expire_minutes

    # Thời điểm token hết hạn = hiện tại + delta
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)

    # Thân Token (payload)
    payload: dict[str, Any] = {
        "sub": subject, # Định danh user
        "exp": expire   # Thời gian hết hạn
    }

    # Nếu có thông tin phụ thì update vào payload
    if extra_claims:
        payload.update(extra_claims)

    # Mã hóa payload thành chuỗi JWT hoàn chỉnh
    token = jwt.encode(
        payload, # Nội dung cần mã hóa
        settings.jwt_secret_key, # khóa bí mật của server (dùng để ký, chỉ server biết)
        algorithm=settings.jwt_algorithm # Thuật toán ký
    )

    return token

# Giải mã và xác thực Token (khi client mang Token đi gọi các API cần bảo mật)
def decode_token(token: str) -> dict[str, Any]:
    try:
        # Cố gắng giải mã Token client gửi lên
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    
    # Lỗi Token hết hạn
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"} # Header chuẩn yêu cầu client cung cấp lại Bearer Token
        ) from exc
    
    # Lỗi Token không hợp lệ
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        ) from exc