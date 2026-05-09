from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.db.models import AlertStatus
from app.db.repositories import AlertStatusRepository
from app.permissions.station_scope import ensure_station_scope


class AlertStatusService:
    def __init__(self, db: Session):
        self.db = db
        self.alert_status_repo = AlertStatusRepository(db)

    # Lấy danh sách trạng thái cảnh báo hiện tại
    def list_alert_status(self, *, current_user) -> list[AlertStatus]:
        # STATION_ADMIN lấy cảnh báo hiện tại của trạm mình
        if current_user.role == UserRole.STATION_ADMIN:
            status_obj = self.alert_status_repo.get_by_station_id(current_user.station_id)
            return [status_obj] if status_obj else [] # Bọc kết quả vào List

        # SUPER_ADMIN lấy cảnh báo hiện tại của tất cả các trạm
        return self.alert_status_repo.list_all()

    # Lấy danh sách trạng thái của 1 trạm 
    def get_alert_status_by_station(self, *, station_id: int, current_user):
        # Đảm bảo current user có quyền trên trạm này
        ensure_station_scope(current_user, station_id)

        status_obj = self.alert_status_repo.get_by_station_id(station_id)
        if not status_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert status not found",
            )

        # Lấy thông tin chi tiết từ bảng alert_event
        latest_event = status_obj.latest_event

        # Làm phẳng dữ liệu
        # Chuyển dữ liệu lồng nhau (Nested) sang Dict phẳng
        return {
            "station_id": status_obj.station_id,
            "latest_event_id": status_obj.latest_event_id,
            "latest_event_timestamp": status_obj.latest_event_timestamp,
            "updated_at": status_obj.updated_at,

            # Trường hợp chưa có sự kiện nào
            "latest_alert_level": latest_event.alert_level if latest_event else None,
            "latest_alert_message": latest_event.alert_message if latest_event else None,
            "latest_risk_score": latest_event.risk_score if latest_event else None,
            "latest_event_type": latest_event.event_type if latest_event else None,
        }