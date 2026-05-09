from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.db.repositories import AlertEventRepository
from app.permissions.station_scope import ensure_station_scope


class AlertEventService:
    def __init__(self, db: Session):
        self.db = db
        self.alert_event_repo = AlertEventRepository(db)

    def list_alert_events(
        self,
        *,
        current_user,
        station_id: int | None = None,
        area_id: int | None = None,
        alert_level: int | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ):
        if current_user.role == UserRole.STATION_ADMIN:
            station_id = current_user.station_id

        return self.alert_event_repo.list_all(
            station_id=station_id,
            area_id=area_id,
            alert_level=alert_level,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset,
        )

    def get_alert_event(
        self,
        *,
        event_id: int,
        timestamp: datetime,
        current_user,
    ):
        event = self.alert_event_repo.get_by_pk(event_id, timestamp)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert event not found",
            )

        ensure_station_scope(current_user, event.station_id)
        return event