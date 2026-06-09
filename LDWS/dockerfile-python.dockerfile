# Sử dụng image Python 3.11 (hoặc thay bằng phiên bản bạn đang dùng trong .python-version)
FROM python:3.13-slim

# Cài đặt các thư viện hệ thống cần thiết (giúp cài đặt psycopg và các thư viện C extensions không bị lỗi)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc trong Container
WORKDIR /app

# Cài đặt trình quản lý gói `uv`
RUN pip install --no-cache-dir uv

# Copy các file quản lý thư viện vào trước để tận dụng Docker Cache
COPY pyproject.toml uv.lock ./

# Cài đặt toàn bộ thư viện (Tạo sẵn .venv bên trong container)
RUN uv sync --frozen

# Copy toàn bộ mã nguồn dự án vào thư mục /app
COPY . .

# Lệnh mặc định (Sẽ bị ghi đè bởi command trong docker-compose)
CMD ["uv", "run", "python", "consumer/mqtt_to_db_worker.py"]