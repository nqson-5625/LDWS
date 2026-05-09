from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

# Lớp tiếp nhận dữ liệu thô
class RawReadingInput(BaseModel):
    timestamp: datetime
    sensor_id: int
    value_1: float | None = None
    value_2: float | None = None
    value_3: float | None = None
    quality_flag: int = 0
    raw_payload: dict[str, Any] | None = None

    # Validator cho timestamp: Xử lý định dạng ISO
    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, value):
        if isinstance(value, datetime): # Nếu đã là datetime
            return value
        
        if isinstance(value, str): # Nếu chưa phải datetime
            # Thay thế "Z" -> "+00:00" => đây là UTC
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        
        raise ValueError("timestamp must be datetime or ISO string")
    
    # Validator cho quality_flag: Đảm bảo chỉ nhận giá trị 0-4
    @field_validator("quality_flag")
    @classmethod
    def validate_quality_flag(cls, value: int) -> int:
        if value not in {0, 1, 2, 3, 4}:
            raise ValueError("quality_flag must be in {0, 1, 2, 3, 4}")
        return value
    
    # Validator toàn bộ model: Đảm bảo tồn tại value
    @model_validator(mode="after")
    def ensure_one_value_exists(self):
        if self.value_1 is None and self.value_2 is None and self.value_3 is None:
            raise ValueError("at least one of value_1/value_2/value_3 must be present")
        return self
    
# Lớp dữ liệu đã làm sạch
class ValidatedReading(BaseModel):
    timestamp: datetime
    area_id: int
    station_id: int
    sensor_id: int
    sensor_type: str
    value_1: float | None = None
    value_2: float | None = None
    value_3: float | None = None
    quality_flag: int = 0
    raw_payload: dict[str, Any] | None = None

    # Chuyển đổi từ Object Pydantic sang dict để SQLAlchemy insert vào DB
    def to_insert_dict(self, reading_id: int) -> dict[str, Any]:
        return {
            "reading_id": reading_id,
            "timestamp": self.timestamp,
            "area_id": self.area_id,
            "station_id": self.station_id,
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type,
            "value_1": self.value_1,
            "value_2": self.value_2,
            "value_3": self.value_3,
            "quality_flag": self.quality_flag,
            "raw_payload": self.raw_payload,
        }

# Các lớp giám sát pipeline 

class PipelineStageStats(BaseModel):
    stage: str # Tên giai đoạn ("Extract", "Transform",...)
    records_in: int = 0 # Số bản ghi đầu vào
    records_out: int = 0 # Số bản ghi sau khi xử lý
    error_count: int = 0
    errors: list[str] = Field(default_factory=list) # Danh sách lỗi
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)) # Lấy thời điểm bắt đầu
    ended_at: datetime | None = None

    # Method ghi lại giờ kết thúc
    def finish(self):
        self.ended_at = datetime.now(timezone.utc)
        return self


class PipelineRunResult(BaseModel):
    # Cấu trúc tổng thể của một lần chạy Pipeline
    pipeline_name: str
    source_name: str
    started_at: datetime
    finished_at: datetime | None = None

    checkpoint_before: datetime | None = None
    checkpoint_after: datetime | None = None

    # Từng giai đoạn cụ thể của pipeline được lưu theo từng object Stats
    extract: PipelineStageStats
    validate: PipelineStageStats
    load_raw: PipelineStageStats
    transform: PipelineStageStats
    publish: PipelineStageStats

    status: str = "running" # Trạng thái chạy (running, success, failed)