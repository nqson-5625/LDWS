from datetime import datetime

from sqlalchemy import func, select
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
    
    def get_max_event_id(self) -> int:
        val = self.db.execute(
            select(func.max(AlertEvent.event_id))
        ).scalar_one_or_none()
        return int(val or 0)
 
    def create(
        self,
        *,
        event_id: int,
        timestamp: datetime,
        area_id: int,
        station_id: int,
        alert_level: int,
        risk_score: float,
        trigger_feature_id: int | None,
        trigger_feature_timestamp: datetime | None,
        alert_message: str,
        event_type: str,
    ) -> AlertEvent:
        event = AlertEvent(
            event_id=event_id,
            timestamp=timestamp,
            area_id=area_id,
            station_id=station_id,
            alert_level=alert_level,
            risk_score=risk_score,
            trigger_feature_id=trigger_feature_id,
            trigger_feature_timestamp=trigger_feature_timestamp,
            alert_message=alert_message,
            event_type=event_type,
            telegram_sent=False,
        )
        self.db.add(event)
        self.db.flush()
        self.db.refresh(event)
        return event
 
    def mark_telegram_sent(self, event: AlertEvent, sent_at: datetime) -> None:
        event.telegram_sent    = True
        event.telegram_sent_at = sent_at
        self.db.flush()