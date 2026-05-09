from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import SensorReading


class SensorReadingRepository:
    def __init__(self, db: Session):
        self.db = db

    # Lấy bản ghi sensor bằng cặp khóa chính
    def get_by_pk(self, reading_id: int, timestamp: datetime) -> SensorReading | None:
        stmt = select(SensorReading).where(
            SensorReading.reading_id == reading_id,
            SensorReading.timestamp == timestamp,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    # Lấy danh sách tất cả các bản ghi sensor với các điều kiện truyền vào
    def list_all(
        self,
        *,
        station_id: int | None = None,
        sensor_id: int | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SensorReading]:
        stmt = select(SensorReading)

        if station_id is not None:
            stmt = stmt.where(SensorReading.station_id == station_id)

        if sensor_id is not None:
            stmt = stmt.where(SensorReading.sensor_id == sensor_id)

        if start_time is not None:
            stmt = stmt.where(SensorReading.timestamp >= start_time)

        if end_time is not None:
            stmt = stmt.where(SensorReading.timestamp <= end_time)

        stmt = (
            stmt.order_by(
                SensorReading.timestamp.desc(), 
                SensorReading.reading_id.desc()
            )
            # Phân trang
            .offset(offset) # Số dòng bỏ qua tính từ dòng trên cùng
            .limit(limit)   # Số dòng tối đa trên 1 trang
        )

        return list(self.db.execute(stmt).scalars().all())
    
    # Lấy reading_id lớn nhất
    def get_max_reading_id(self) -> int:
        stmt = select(func.max(SensorReading.reading_id))
        value = self.db.execute(stmt).scalar_one_or_none()
        return int(value or 0) # Nếu value = None thì trả về 0
    
    # Lấy timestamp mới nhất dựa trên station hoặc sensor
    def get_latest_timestamp(
        self,
        *,
        station_id: int | None = None,
        sensor_id: int | None = None
    ) -> datetime | None:
        stmt = select(func.max(SensorReading.timestamp))

        if station_id is not None:
            stmt = stmt.where(SensorReading.station_id == station_id)

        if sensor_id is not None:
            stmt = stmt.where(SensorReading.sensor_id == sensor_id)

        return self.db.execute(stmt).scalar_one_or_none()
    
    # Kiểm tra sự tồn tại
    def exists_for_sensor_timestamp(self, *, sensor_id: int, timestamp: datetime) -> bool:
        stmt = (
            select(SensorReading.reading_id)
            .where(SensorReading.sensor_id == sensor_id, SensorReading.timestamp == timestamp)
            .limit(1) # dừng ngay khi thấy bản ghi đầu tiên
        )
        return self.db.execute(stmt).scalar_one_or_none() is not None
    
    # Thêm dữ liệu hàng loạt (Bulk Insert)
    def bulk_insert(self, rows: list[dict]) -> int:
        if not rows:
            return 0
        
        # Chuyển list[dict] => list[object]
        objects = []
        for row in rows:
            obj = SensorReading(**row) # **row: giải nén dict
            objects.append(obj)

        try:
            self.db.add_all(objects)
            self.db.commit()
            return len(objects)
        except Exception:
            self.db.rollback()
            raise