from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.db.models import DerivedFeature
from app.db.repositories import DerivedFeatureRepository
from app.permissions.station_scope import ensure_station_scope
from app.schemas.derived_feature import DerivedFeatureCreate


class DerivedFeatureService:
    def __init__(self, db: Session):
        self.db = db
        self.derived_feature_repo = DerivedFeatureRepository(db)

    # (SUPER_ADMIN / STATION_ADMIN) lấy danh sách đặc trưng dẫn xuất
    def list_derived_features(
        self,
        *,
        current_user,
        station_id: int | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ):
        # STATION_ADMIN chỉ được xem dữ liệu của trạm mình
        if current_user.role == UserRole.STATION_ADMIN:
            station_id = current_user.station_id

        return self.derived_feature_repo.list_all(
            station_id=station_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset,
        )
    
    # Lấy thông tin đặc trưng dẫn xuất
    def get_derived_feature(
        self,
        *,
        feature_id: int,
        timestamp: datetime,
        current_user,
    ):
        feature = self.derived_feature_repo.get_by_pk(feature_id, timestamp)
        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Derived feature not found",
            )

        # Đảm bảo current user có quyền hạn với bản ghi này
        ensure_station_scope(current_user, feature.station_id)
        return feature

    def upsert_derived_feature(self, payload: DerivedFeatureCreate) -> DerivedFeature:
        try:
            feature = self.derived_feature_repo.upsert(payload)
            self.db.commit()
            self.db.refresh(feature)
            return feature
        except Exception:
            self.db.rollback()
            raise