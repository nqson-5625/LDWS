from pydantic_settings import BaseSettings, SettingsConfigDict

# BaseSettings: class chuyên dùng để đọc config từ biến môi trường (ENV) và file .env
# SettingsConfigDict: nơi cấu hình cách load

class Settings(BaseSettings): # class Settings kế thừa từ BaseSettings -> tự động đọc ENV
    app_name: str 
    app_version: str 
    database_url: str
    debug: bool 

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Tránh crash nếu có biến dư
    )

settings = Settings() # Tạo object