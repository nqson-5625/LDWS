from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.schemas.derived_feature import DerivedFeatureResponse
from app.services.derived_feature_service import DerivedFeatureService

router = APIRouter(prefix="/v1/derived-features", tags=["derived_features"])

# API lấy danh sách đặc trưng dẫn xuất
@router.get("", response_model=list[DerivedFeatureResponse])
def list_derived_features(
    station_id: int | None = Query(default=None, description="Lọc theo ID trạm"),
    start_time: datetime | None = Query(default=None, description="Thời điểm bắt đầu (ISO Format)"),
    end_time: datetime | None = Query(default=None, description="Thời điểm kết thúc (ISO Format)"),

    # Phân trang
    limit: int = Query(default=100, ge=1, le=500), # 1 <= limit <= 500
    offset: int = Query(default=0, ge=0), # 0 <= offset

    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    # Trả về danh sách đặc trưng dẫn xuất theo điều kiện
    return DerivedFeatureService(db).list_derived_features(
        current_user=current_user,
        station_id=station_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset,
    )


@router.get("/{feature_id}", response_model=DerivedFeatureResponse)
def get_derived_feature(
    feature_id: int,
    timestamp: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return DerivedFeatureService(db).get_derived_feature(
        feature_id=feature_id,
        timestamp=timestamp,
        current_user=current_user,
    )