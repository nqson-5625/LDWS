from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.db.repositories import DashboardRepository


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.dashboard_repo = DashboardRepository(db)

    # Hàm tổng hợp dữ liệu cho Dashboard
    def get_summary(self, *, current_user, station_id: int | None = None):
        # STATION_ADMIN chỉ có quyền trên trạm của mình
        if current_user.role == UserRole.STATION_ADMIN:
            station_id = current_user.station_id

        # Lấy số lượng cảm biến
        total_sensors = self.dashboard_repo.count_sensors(station_id=station_id)
        # Lấy số lượng cảm biến hoạt động
        active_sensors = self.dashboard_repo.count_active_sensors(station_id=station_id)

        # Lấy số lượng cảnh báo trong 24h qua
        recent_alert_count = self.dashboard_repo.count_recent_alert_events(
            station_id=station_id,
            since=(datetime.now(timezone.utc) - timedelta(hours=24))
        )

        # Lấy danh sách trạng thái cảnh báo hiện tại
        alert_status_rows = self.dashboard_repo.get_alert_status_rows(station_id=station_id)
        # Lấy danh sách bản ghi mới nhất
        latest_readings = self.dashboard_repo.get_latest_sensor_readings(
            station_id=station_id,
            limit=10,
        )

        # Gom nhóm và ánh xạ dữ liệu
        return {
            "station_id": station_id,
            "total_sensors": total_sensors,
            "active_sensors": active_sensors,
            "recent_alert_count": recent_alert_count,
            "alert_status_count": len(alert_status_rows),
            "latest_readings": [
                {
                    "reading_id": row.reading_id,
                    "timestamp": row.timestamp,
                    "station_id": row.station_id,
                    "sensor_id": row.sensor_id,
                    "sensor_type": row.sensor_type,
                    "value_1": row.value_1,
                    "value_2": row.value_2,
                    "value_3": row.value_3,
                    "quality_flag": row.quality_flag,
                }
                for row in latest_readings
            ],
        }