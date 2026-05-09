from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import DerivedFeature


class DerivedFeatureRepository:
    def __init__(self, db: Session):
        self.db = db

    # Lấy thông tin đặc trưng dẫn xuất bằng cặp khóa chính
    def get_by_pk(self, feature_id: int, timestamp: datetime) -> DerivedFeature | None:
        stmt = select(DerivedFeature).where(
            DerivedFeature.feature_id == feature_id,
            DerivedFeature.timestamp == timestamp,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    # Lấy danh sách các đặc trưng dẫn xuất theo các điều kiện truyền vào
    def list_all(
        self,
        *,
        station_id: int | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DerivedFeature]:
        stmt = select(DerivedFeature)

        if station_id is not None:
            stmt = stmt.where(DerivedFeature.station_id == station_id)

        if start_time is not None:
            stmt = stmt.where(DerivedFeature.timestamp >= start_time)

        if end_time is not None:
            stmt = stmt.where(DerivedFeature.timestamp <= end_time)

        stmt = (
            stmt.order_by(
                DerivedFeature.timestamp.desc(), 
                DerivedFeature.feature_id.desc()
            )
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())