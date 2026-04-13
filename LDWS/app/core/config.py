from pydantic_settings import BaseSettings, SettingsConfigDict

# BaseSettings: class chuyên dùng để đọc config từ biến môi trường (ENV) và file .env
# SettingsConfigDict: nơi cấu hình cách load

class Settings(BaseSettings): # class Settings kế thừa từ BaseSettings -> tự động đọc ENV
    app_name: str 
    app_version: str 
    database_url: str
    debug: bool 

    jwt_secret_key: str # Khóa bí mật dùng để sign và verify JWT
    jwt_algorithm: str  # Thuật toán dùng để mã hóa JWT
    jwt_access_token_expire_minutes: int    # Thời gian sống của access token 
                                            # Sau thời gian này, user phải login lại hoặc refresh token

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Tránh crash nếu có biến dư
    )

settings = Settings() # Tạo object