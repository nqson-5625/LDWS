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
    
    # Postgres Settings
    postgres_host: str | None = None
    postgres_port: int | None = None
    internal_postgres_host: str | None = None
    internal_postgres_port: int | None = None
    postgres_user: str | None = None
    postgres_password: str | None = None
    postgres_db: str | None = None

    # MinIO Settings
    minio_root_user: str | None = None
    minio_root_password: str | None = None
    minio_endpoint: str | None = None
    internal_minio_endpoint: str | None = None
    minio_access_key: str | None = None
    minio_secret_key: str | None = None
    minio_bucket: str | None = None
    minio_local_dir: str | None = None

    # Airflow DB Settings
    airflow_db_user: str | None = None
    airflow_db_password: str | None = None
    airflow_db_name: str | None = None

    # Airflow Webserver Settings
    airflow_webserver_user: str | None = None
    airflow_webserver_firstname: str | None = None
    airflow_webserver_lastname: str | None = None
    airflow_webserver_email: str | None = None
    airflow_webserver_password: str | None = None

    # Kafka Settings
    kafka_bootstrap: str | None = None
    kafka_group: str | None = None

    # Snowflake Settings
    snowflake_user: str | None = None
    snowflake_password: str | None = None
    snowflake_account: str | None = None
    snowflake_warehouse: str | None = None
    snowflake_db: str | None = None
    snowflake_schema: str | None = None

    # MQTT Settings
    mqtt_broker: str | None = None
    mqtt_port: int | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Tránh crash nếu có biến dư
    )

settings = Settings() # Tạo object