from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Area

class AreaRepository:
    def __init__(self, db: Session):
        self.db = db

    # Lấy Area theo ID
    def get_by_id(self, area_id: int) -> Area | None:
        stmt = select(Area).where(Area.area_id == area_id)
        return self.db.execute(stmt).scalar_one_or_none()
    
    # Lấy Area theo name
    def get_by_name(self, area_name: str) -> Area | None:
        stmt = select(Area).where(Area.area_name == area_name)
        return self.db.execute(stmt).scalar_one_or_none()
    
    # Lấy tất cả Area
    def list_all(self) -> list[Area]:
        stmt = select(Area).order_by(Area.area_id.asc())
        return list(self.db.execute(stmt).scalars().all())
    
    # Tạo Area
    def create(self, **kwargs) -> Area:
        area = Area(**kwargs)
        
        try:
            self.db.add(area)
            self.db.flush()
            self.db.refresh(area)
            self.db.commit()
            return area
        except Exception:
            self.db.rollback()
            raise

    # Tạo area -> telegram_channel trong cùng 1 transaction ở service
    def create_in_tx(self, **kwargs) -> Area:
        area = Area(**kwargs)
        self.db.add(area)
        self.db.flush()   # lấy area_id ngay trong transaction
        self.db.refresh(area)
        return area

    # Cập nhật Area
    def update(self, area: Area, **kwargs) -> Area:
        try:
            for key, value in kwargs.items(): # Lặp qua tất cả các item trong dict kwargs
                setattr(area, key, value) # Thiết lập thuộc tính cho object
            
            self.db.add(area)
            self.db.flush()
            self.db.refresh(area)
            self.db.commit()
            return area
        except Exception:
            self.db.rollback()
            raise

    # Xóa Area
    def delete(self, area: Area) -> None:
        try:
            self.db.delete(area)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise