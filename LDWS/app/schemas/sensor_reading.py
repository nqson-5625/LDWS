from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SensorReadingBase(BaseModel):
    reading_id: int
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
    created_at: datetime

class SensorReadingResponse(SensorReadingBase):
    model_config = ConfigDict(from_attributes=True)