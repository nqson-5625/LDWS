from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.schemas.alert_event import AlertEventResponse
from app.services.alert_event_service import AlertEventService

router = APIRouter(prefix="/v1/alert-events", tags=["alert_events"])

# API truy vấn lịch sử cảnh báo
@router.get("/", response_model=list[AlertEventResponse])
def list_alert_events(
    station_id: int | None = Query(default=None, description="Lọc theo ID trạm"),
    area_id: int | None = Query(default=None, description="Lọc theo ID khu vực"),
    alert_level: int | None = Query(default=None, description="Lọc theo mức cảnh báo"),
    start_time: datetime | None = Query(default=None, description="Thời điểm bắt đầu (ISO Format)"),
    end_time: datetime | None = Query(default=None, description="Thời điểm kết thúc (ISO Format)"),

    # Phân trang
    limit: int = Query(default=100, ge=1, le=500), # 1 <= limit <= 500
    offset: int = Query(default=0, ge=0), # 0 <= offset

    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return AlertEventService(db).list_alert_events(
        current_user=current_user,
        station_id=station_id,
        area_id=area_id,
        alert_level=alert_level,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset,
    )

# API lấy chi tiết 1 sự kiện cảnh báo
@router.get("/{event_id}", response_model=AlertEventResponse)
def get_alert_event(
    event_id: int,
    timestamp: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return AlertEventService(db).get_alert_event(
        event_id=event_id,
        timestamp=timestamp,
        current_user=current_user,
    )