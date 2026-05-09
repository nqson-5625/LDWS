from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import SensorStatus


class SensorBase(BaseModel):
    type_code: str
    sensor_code: str | None = None
    sensor_name: str
    install_position: str | None = None
    status: SensorStatus = SensorStatus.ACTIVE


class SensorCreate(SensorBase):
    # super_admin có thể truyền station_id
    # station_admin không cần truyền, service sẽ tự xác định station_id của station_admin để truyền vào
    station_id: int | None = None


class SensorUpdate(BaseModel):
    station_id: int | None = None
    type_code: str | None = None
    sensor_code: str | None = None
    sensor_name: str | None = None
    install_position: str | None = None
    status: SensorStatus | None = None


class SensorStatusUpdate(BaseModel):
    status: SensorStatus


class SensorResponse(SensorBase):
    sensor_id: int
    station_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)