from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.db.repositories import SensorReadingRepository
from app.permissions.station_scope import ensure_station_scope


class SensorReadingService:
    def __init__(self, db: Session):
        self.db = db
        self.sensor_reading_repo = SensorReadingRepository(db)

    def list_sensor_readings(
        self,
        *,
        current_user,
        station_id: int | None = None,
        sensor_id: int | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ):
        # Nếu là STATION_ADMIN thì chỉ được lấy của trạm mình
        if current_user.role == UserRole.STATION_ADMIN:
            station_id = current_user.station_id

        return self.sensor_reading_repo.list_all(
            station_id=station_id,
            sensor_id=sensor_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset,
        )

    def get_sensor_reading(
        self,
        *,
        reading_id: int,
        timestamp: datetime,
        current_user,
    ):
        reading = self.sensor_reading_repo.get_by_pk(reading_id, timestamp)
        if not reading:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sensor reading not found",
            )

        # Đảm bảo current user có quyền trên bản ghi này
        ensure_station_scope(current_user, reading.station_id)
        return reading