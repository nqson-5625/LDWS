from datetime import datetime

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.db.models import DerivedFeature
from app.schemas.derived_feature import DerivedFeatureCreate


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
    
    def get_latest_by_station(self, station_id: int) -> DerivedFeature | None:
        stmt = (
            select(DerivedFeature)
            .where(DerivedFeature.station_id == station_id)
            .order_by(
                DerivedFeature.timestamp.desc(),
                DerivedFeature.feature_id.desc(),
            )
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()
 
    def upsert(self, derived_feature: DerivedFeatureCreate) -> DerivedFeature:
        existing = self.get_by_pk(derived_feature.feature_id, derived_feature.timestamp)
        if existing:
            # model_dump(): chuyển Pydantic model thành dict, exclude: loại bỏ các trường không cần cập nhật
            update_fields = derived_feature.model_dump(exclude={"feature_id", "timestamp"}) 
            for field, value in update_fields.items():
                setattr(existing, field, value) # Thiết lập lại giá trị cho các trường cần cập nhật
            self.db.add(existing) # Đánh dấu object đã thay đổi để SQLAlchemy tự động sinh câu UPDATE khi flush/commit
        else:
            existing = DerivedFeature(**derived_feature.model_dump()) # **: giải nén dict thành các tham số khi khởi tạo object
            self.db.add(existing)
        self.db.flush()
        return existing

    def list_latest_by_area(self, area_id: int) -> list[DerivedFeature]:
        sql = text("""
            SELECT DISTINCT ON (df.station_id)
                df.*
            FROM derived_features df
            JOIN stations st ON st.station_id = df.station_id
            WHERE st.area_id = :area_id
              AND st.status  = 'active'
            ORDER BY df.station_id, df.timestamp DESC, df.feature_id DESC
        """)
        rows = self.db.execute(sql, {"area_id": area_id}).fetchall()
        return [
            self.db.get(DerivedFeature, (row.feature_id, row.timestamp))
            for row in rows
        ]