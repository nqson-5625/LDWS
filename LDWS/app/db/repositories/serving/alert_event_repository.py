from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AlertEvent


class AlertEventRepository:
    def __init__(self, db: Session):
        self.db = db

    # Lấy thông tin sự kiện cảnh báo bằng cặp khóa chính
    def get_by_pk(self, event_id: int, timestamp: datetime) -> AlertEvent | None:
        stmt = select(AlertEvent).where(
            AlertEvent.event_id == event_id,
            AlertEvent.timestamp == timestamp,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    # Lấy danh sách sự kiện cảnh báo theo các điều kiện truyền vào
    def list_all(
        self,
        *,
        station_id: int | None = None,
        area_id: int | None = None,
        alert_level: int | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AlertEvent]:
        stmt = select(AlertEvent)

        if station_id is not None:
            stmt = stmt.where(AlertEvent.station_id == station_id)

        if area_id is not None:
            stmt = stmt.where(AlertEvent.area_id == area_id)

        if alert_level is not None:
            stmt = stmt.where(AlertEvent.alert_level == alert_level)

        if start_time is not None:
            stmt = stmt.where(AlertEvent.timestamp >= start_time)

        if end_time is not None:
            stmt = stmt.where(AlertEvent.timestamp <= end_time)

        stmt = (
            stmt.order_by(AlertEvent.timestamp.desc(), AlertEvent.event_id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())
    
    # Lấy danh sách các sự kiện chưa được gửi thông báo qua Telegram
    def list_recent_unsent_candidates(
        self,
        *,
        area_id: int | None = None,
        limit: int = 50,
    ) -> list[AlertEvent]:
        stmt = select(AlertEvent).where(AlertEvent.telegram_sent.is_(False))

        if area_id is not None:
            stmt = stmt.where(AlertEvent.area_id == area_id)

        stmt = stmt.order_by(
            AlertEvent.timestamp.asc(),
            AlertEvent.event_id.asc(),
        ).limit(limit)

        return list(self.db.execute(stmt).scalars().all())