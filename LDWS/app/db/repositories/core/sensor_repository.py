from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Sensor

class SensorRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, sensor_id: int) -> Sensor | None:
        stmt = select(Sensor).where(Sensor.sensor_id == sensor_id)
        return self.db.execute(stmt).scalar_one_or_none()
    
    # Lấy Sensor bằng sensor_code (mã phần cứng)
    def get_by_sensor_code(self, sensor_code: str) -> Sensor | None:
        stmt = select(Sensor).where(Sensor.sensor_code == sensor_code)
        return self.db.execute(stmt).scalar_one_or_none()
    
    # Lấy Sensor theo loại cảm biến (sensor_type)
    def get_by_type_code(self, type_code: str) -> list[Sensor]:
        stmt = select(Sensor).where(Sensor.type_code == type_code).order_by(Sensor.sensor_id.asc())
        return list(self.db.execute(stmt).scalars().all())
    
    def list_all(self) -> list[Sensor]:
        stmt = select(Sensor).order_by(Sensor.sensor_id.asc())
        return list(self.db.execute(stmt).scalars().all())
    
    # Lấy danh sách tất cả Sensor đang hoạt động (active)
    def list_active(self) -> list[Sensor]:
        stmt = select(Sensor).where(Sensor.status == 'active').order_by(Sensor.sensor_id.asc())
        return list(self.db.execute(stmt).scalars().all())
    
    # Lấy danh sách Sensor theo trạm
    def list_by_station(self, station_id: int) -> list[Sensor]:
        stmt = select(Sensor).where(Sensor.station_id == station_id).order_by(Sensor.sensor_id.asc())
        return list(self.db.execute(stmt).scalars().all())
    
    def create(self, **kwargs) -> Sensor:
        sensor = Sensor(**kwargs)
        try:
            self.db.add(sensor)
            self.db.flush()
            self.db.refresh(sensor)
            self.db.commit()
            return sensor
        except Exception:
            self.db.rollback()
            raise

    def update(self, sensor: Sensor, **kwargs) -> Sensor:
        try:
            for key, value in kwargs.items():
                setattr(sensor, key, value)
            self.db.add(sensor)
            self.db.flush()
            self.db.refresh(sensor)
            self.db.commit()
            return sensor
        except Exception:
            self.db.rollback()
            raise

    def delete(self, sensor: Sensor) -> None:
        try:
            self.db.delete(sensor)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise