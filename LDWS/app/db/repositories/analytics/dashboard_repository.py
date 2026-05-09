from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.db.models import AlertEvent, AlertStatus, Sensor, SensorReading


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    # Hàm đếm số lượng sensors hiện có
    # SUPER_ADMIN (station_id = None) => Đếm số lượng tất cả sensors toàn hệ thống
    # STATION_ADMIN (station_id != None) => Đếm số lượng tất cả sensors của trạm mình
    def count_sensors(self, station_id: int | None = None) -> int:
        stmt = select(func.count(Sensor.sensor_id))
        if station_id is not None:
            stmt = stmt.where(Sensor.station_id == station_id)
        return int(self.db.execute(stmt).scalar_one())

    # Hàm (SUPER_ADMIN / STATION_ADMIN) đếm số lượng sensors đang hoạt động
    def count_active_sensors(self, station_id: int | None = None) -> int:
        stmt = select(func.count(Sensor.sensor_id)).where(Sensor.status == "active")
        if station_id is not None:
            stmt = stmt.where(Sensor.station_id == station_id)
        return int(self.db.execute(stmt).scalar_one())

    # Hàm (SUPER_ADMIN / STATION_ADMIN) đếm số lượng các sự kiện cảnh báo kể từ thời điểm 'since'
    def count_recent_alert_events(self, station_id: int | None = None, since: datetime | None = None) -> int:
        stmt = select(func.count(AlertEvent.event_id))
        if station_id is not None:
            stmt = stmt.where(AlertEvent.station_id == station_id)

        if since is not None:
            stmt = stmt.where(AlertEvent.timestamp >= since)

        return int(self.db.execute(stmt).scalar_one())

    # Hàm (SUPER_ADMIN / STATION_ADMIN) lấy danh sách sự kiện cảnh báo hiện tại
    def get_alert_status_rows(self, station_id: int | None = None) -> list[AlertStatus]:
        stmt = (
            select(AlertStatus)
            # Eager loading - Nạp dữ liệu sớm
            .options(joinedload(AlertStatus.latest_event))
            .order_by(AlertStatus.station_id.asc())
        )
        if station_id is not None:
            stmt = stmt.where(AlertStatus.station_id == station_id)
        return list(self.db.execute(stmt).scalars().all())

    # Lấy danh sách bản ghi mới nhất
    def get_latest_sensor_readings(
        self,
        *,
        station_id: int | None = None,
        limit: int = 10, # Số lượng bản ghi tối đa được lấy
    ) -> list[SensorReading]:
        stmt = select(SensorReading)

        if station_id is not None:
            stmt = stmt.where(SensorReading.station_id == station_id)

        stmt = stmt.order_by(
            SensorReading.timestamp.desc(),
            SensorReading.reading_id.desc(),
        ).limit(limit)

        return list(self.db.execute(stmt).scalars().all())