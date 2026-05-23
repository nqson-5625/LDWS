from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class SensorReadingBase(BaseModel):
    timestamp: datetime
    area_id: int
    station_id: int
    sensor_id: int
    sensor_type: str
    value_1: float | None = None
    value_2: float | None = None
    value_3: float | None = None
    quality_flag: int
    raw_payload: dict | None = None

class SensorReadingCreate(SensorReadingBase):
    quality_flag: int = 0
 
    @field_validator("quality_flag")
    @classmethod
    def validate_quality_flag(cls, v: int) -> int:
        if v not in (0, 1, 2, 3, 4):
            raise ValueError("quality_flag phải là 0, 1, 2, 3 hoặc 4")
        return v
 
    @field_validator("sensor_type")
    @classmethod
    def validate_sensor_type(cls, v: str) -> str:
        allowed = {"rain", "tilt", "vibration", "displacement", "temperature"}
        if v not in allowed:
            raise ValueError(f"sensor_type không hợp lệ: {v!r}")
        return v

class SensorReadingResponse(SensorReadingBase):
    reading_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)