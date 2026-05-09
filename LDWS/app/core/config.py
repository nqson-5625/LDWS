from pydantic_settings import BaseSettings, SettingsConfigDict

# BaseSettings: class chuyên dùng để đọc config từ biến môi trường (ENV) và file .env
# SettingsConfigDict: nơi cấu hình cách load

class Settings(BaseSettings): # class Settings kế thừa từ BaseSettings -> tự động đọc ENV
    app_name: str 
    app_version: str 
    database_url: str
    debug: bool 

    # jwt settings
    jwt_secret_key: str # Khóa bí mật dùng để sign và verify JWT
    jwt_algorithm: str  # Thuật toán dùng để mã hóa JWT
    jwt_access_token_expire_minutes: int    # Thời gian sống của access token 
                                            # Sau thời gian này, user phải login lại hoặc refresh token

    # Telegram settings
    telegram_enabled: bool = False # Có cho tích hợp Telegram không
    telegram_bot_token: str | None = None
    telegram_api_base_url: str = "https://api.telegram.org"
    telegram_disable_notification: bool = False # Gửi im lặng hay kèm cảnh báo
    telegram_parse_mode: str = "HTML"
    telegram_delivery_state_file: str = "storage/telegram_delivery_logs/delivery_state.json"

    # pipeline settings
    pipeline_default_source: str = "simulated" # nguồn dữ liệu mặc định
    pipeline_log_level: str = "INFO" # mức độ chi tiết của log
    pipeline_checkpoint_dir: str = "storage/checkpoints" # đường dẫn đến nơi lưu các file checkpoint
    pipeline_batch_size: int = 500 # số lượng bản ghi xử lý mỗi đợt (batch)

    pipeline_default_csv_path: str = "storage/temp/sample_sensor_readings.csv"
    pipeline_default_gateway_payload_path: str = "storage/temp/gateway_payload.json"
    pipeline_default_api_url: str = "http://host.docker.internal:9001/mock-sensor-readings"

    # Cấu hình lưu trữ MinIO: nơi hệ thống đẩy dữ liệu thô lên sau khi xử lý
    minio_endpoint: str | None = None 
    minio_access_key: str | None = None
    minio_secret_key: str | None = None
    minio_bucket_raw: str = "ldws-raw"

    airflow_enabled: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Tránh crash nếu có biến dư
    )

settings = Settings() # Tạo object