from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.schemas.alert_status import AlertStatusDetailResponse, AlertStatusResponse
from app.services.alert_status_service import AlertStatusService

router = APIRouter(prefix="/v1/alert-status", tags=["alert_status"])

# API lấy danh sách trạng thái hiện tại của tất cả các trạm
@router.get("/", response_model=list[AlertStatusResponse])
def list_alert_status(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return AlertStatusService(db).list_alert_status(current_user=current_user)

# API lấy chi tiết trạng thái của 1 trạm
@router.get("/stations/{station_id}", response_model=AlertStatusDetailResponse)
def get_alert_status_by_station(
    station_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return AlertStatusService(db).get_alert_status_by_station(
        station_id=station_id,
        current_user=current_user,
    )