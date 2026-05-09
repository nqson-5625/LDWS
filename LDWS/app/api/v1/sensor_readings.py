from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.schemas.sensor_reading import SensorReadingResponse
from app.services.sensor_reading_service import SensorReadingService

router = APIRouter(prefix="/v1/sensor-readings", tags=["sensor_readings"])

# API lấy danh sách dữ liệu đo đạc
@router.get("/", response_model=list[SensorReadingResponse])
def list_sensor_readings(
    station_id: int | None = Query(default=None, description="Lọc theo ID trạm"),
    sensor_id: int | None = Query(default=None, description="Lọc theo ID cảm biến"),
    start_time: datetime | None = Query(default=None, description="Thời điểm bắt đầu (ISO Format)"),
    end_time: datetime | None = Query(default=None, description="Thời điểm kết thúc (ISO Format)"),

    # Phân trang
    limit: int = Query(default=100, ge=1, le=500), # 1 <= limit <= 500
    offset: int = Query(default=0, ge=0), # 0 <= offset

    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    # Lấy danh sách bản ghi theo điều kiện
    return SensorReadingService(db).list_sensor_readings(
        current_user=current_user,
        station_id=station_id,
        sensor_id=sensor_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset
    )

# API lấy chi tiết dữ liệu của 1 bản ghi
@router.get("/{reading_id}", response_model=SensorReadingResponse)
def get_sensor_reading(
    reading_id: int,
    timestamp: datetime = Query(...), # ... là bắt buộc phải điền

    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return SensorReadingService(db).get_sensor_reading(
        reading_id=reading_id,
        timestamp=timestamp,
        current_user=current_user,
    )