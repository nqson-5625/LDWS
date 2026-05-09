from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.models import AlertStatus

class AlertStatusRepository:
    def __init__(self, db: Session):
        self.db = db

    # Lấy thông tin cảnh báo hiện tại theo station_id
    def get_by_station_id(self, station_id: int) -> AlertStatus | None:
        stmt = (
            select(AlertStatus)

            # Eager loading - Nạp dữ liệu sớm => Chống N+1 query
            # Tự động JOIN gom toàn bộ latest_event về ngay lập tức
            .options(joinedload(AlertStatus.latest_event))
            .where(AlertStatus.station_id == station_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    # Lấy thông tin cảnh báo hiện tại của tất cả các trạm
    def list_all(self) -> list[AlertStatus]:
        stmt = (
            select(AlertStatus)
            .options(joinedload(AlertStatus.latest_event))
            .order_by(AlertStatus.station_id.asc())
        )
        return list(self.db.execute(stmt).scalars().all())