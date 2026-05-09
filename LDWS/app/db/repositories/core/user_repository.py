from sqlalchemy import select
from sqlalchemy.orm import Session # Đại diện cho 1 phiên làm việc với db

from app.core.enums import UserRole
from app.db.models import User

class UserRepository:
    # Constructor, cần truyền vào 1 phiên làm việc
    def __init__(self, db: Session):
        self.db = db # Lưu Session vào biến self.db

    # Lấy danh sách tất cả user
    def list_all(self) -> list[User]:
        stmt = select(User).order_by(User.user_id.asc())
        return list(self.db.execute(stmt).scalars().all()) # Lấy tất cả và đưa vào List
    
    # Lấy danh sách tất cả các station_admin
    def list_station_admins(self) -> list[User]:
        stmt = (select(User).where(User.role == UserRole.STATION_ADMIN).order_by(User.user_id.asc()))
        return list(self.db.execute(stmt).scalars().all())

    # Lấy user theo username
    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self.db.execute(stmt).scalar_one_or_none() # trả về object (nếu thấy) hoặc None

    # Lấy user theo ID
    def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()
    
    # Tạo user mới và lưu vào DB
    def create(
        self,
        *, # bắt buộc truyền tên tham số
        username: str,
        password_hash: str,
        role: str,
        station_id: int | None = None,
        is_active: bool = True
    ) -> User:
        # Tạo object User trên RAM (chưa lưu DB)
        user = User(
            username=username,
            password_hash=password_hash,
            role=role,
            station_id=station_id,
            is_active=is_active
        )

        try:
            self.db.add(user)
            self.db.flush() # Đẩy INSERT xuống DB lấy FK tự sinh
            self.db.refresh(user) # Nạp lại dữ liệu
            self.db.commit()
            return user
        except Exception:
            self.db.rollback()
            raise
    
    # Cập nhật user
    def update(self, user: User, **kwargs) -> User:
        try:
            for key, value in kwargs.items():
                setattr(user, key, value)

            self.db.add(user)
            self.db.flush()
            self.db.refresh(user)
            self.db.commit()
            return user
        except Exception:
            self.db.rollback()
            raise