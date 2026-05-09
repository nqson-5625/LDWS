from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import SensorType

class SensorTypeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_code(self, type_code: str) -> SensorType | None:
        stmt = select(SensorType).where(SensorType.type_code == type_code)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def get_by_name(self, type_name: str) -> SensorType | None:
        stmt = select(SensorType).where(SensorType.type_name == type_name)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def list_all(self) -> list[SensorType]:
        stmt = select(SensorType).order_by(SensorType.type_code.asc())
        return list(self.db.execute(stmt).scalars().all())
    
    def create(self, **kwargs) -> SensorType:
        sensor_type = SensorType(**kwargs)
        try:
            self.db.add(sensor_type)
            self.db.flush()
            self.db.refresh(sensor_type)
            self.db.commit()
            return sensor_type
        except Exception:
            self.db.rollback()
            raise

    def update(self, sensor_type: SensorType, **kwargs) -> SensorType:
        try:
            for key, value in kwargs.items():
                setattr(sensor_type, key, value)
            self.db.add(sensor_type)
            self.db.flush()
            self.db.refresh(sensor_type)
            self.db.commit()
            return sensor_type
        except Exception:
            self.db.rollback()
            raise

    def delete(self, sensor_type: SensorType) -> None:
        try:
            self.db.delete(sensor_type)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise