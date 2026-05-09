from datetime import datetime

from pydantic import BaseModel, ConfigDict

class SensorTypeBase(BaseModel):
    type_name: str
    unit_1_name: str | None = None
    unit_1_symbol: str | None = None
    unit_2_name: str | None = None
    unit_2_symbol: str | None = None
    unit_3_name: str | None = None
    unit_3_symbol: str | None = None
    description: str | None = None


class SensorTypeCreate(SensorTypeBase):
    type_code: str


class SensorTypeUpdate(BaseModel):
    type_name: str | None = None
    unit_1_name: str | None = None
    unit_1_symbol: str | None = None
    unit_2_name: str | None = None
    unit_2_symbol: str | None = None
    unit_3_name: str | None = None
    unit_3_symbol: str | None = None
    description: str | None = None


class SensorTypeResponse(SensorTypeBase):
    type_code: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)