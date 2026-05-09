from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import ActiveInactiveStatus

class AreaBase(BaseModel):
    area_name: str
    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    status: ActiveInactiveStatus = ActiveInactiveStatus.ACTIVE

class AreaCreate(AreaBase):
    pass

class AreaUpdate(BaseModel):
    area_name: str | None = None
    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    status: ActiveInactiveStatus | None = None

class AreaResponse(AreaBase):
    area_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)