from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import ActiveInactiveStatus

class StationBase(BaseModel):
    area_id: int
    station_name: str
    location_description: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    elevation: float | None = None
    status: ActiveInactiveStatus = ActiveInactiveStatus.ACTIVE

class StationCreate(StationBase):
    pass

class StationUpdate(BaseModel):
    area_id: int | None = None
    station_name: str | None = None
    location_description: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    elevation: float | None = None
    status: ActiveInactiveStatus | None = None

class StationResponse(StationBase):
    station_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)