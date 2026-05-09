from datetime import datetime

from pydantic import BaseModel, ConfigDict

class AlertStatusBase(BaseModel):
    station_id: int
    latest_event_id: int
    latest_event_timestamp: datetime
    updated_at: datetime

class AlertStatusResponse(AlertStatusBase):
    model_config = ConfigDict(from_attributes=True)


class AlertStatusDetailResponse(AlertStatusBase):
    latest_alert_level: int | None = None
    latest_alert_message: str | None = None
    latest_risk_score: float | None = None
    latest_event_type: str | None = None

    model_config = ConfigDict(from_attributes=True)