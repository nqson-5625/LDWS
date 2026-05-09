from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/v1/dashboard", tags=["dashboard"])

# API tổng hợp số lượng Dashboard
@router.get("/summary")
def get_dashboard_summary(
    # Cho phép SUPER_ADMIN xem Dashboard của từng trạm cụ thể
    station_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return DashboardService(db).get_summary(
        current_user=current_user,
        station_id=station_id,
    )