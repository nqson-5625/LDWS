from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Tạo cầu nối giữa app và db
engine = create_engine(settings.database_url, future=True)

SessionLocal = sessionmaker(
    bind = engine,      # Gắn session với db
    autoflush=False,    # Không tự flush dữ liệu xuống db
    autocommit=False,   # Không tự commit
    future=True,        # Dùng API mới
)

def get_db(): # Cung cấp session cho API
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # Trả connection về pool