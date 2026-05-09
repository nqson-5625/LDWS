from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import AlertEventType


class AlertEventBase(BaseModel):
    event_id: int
    timestamp: datetime
    area_id: int
    station_id: int
    alert_level: int
    risk_score: float | None = None

    trigger_feature_id: int | None = None
    trigger_feature_timestamp: datetime | None = None

    alert_message: str | None = None
    event_type: AlertEventType

    telegram_sent: bool
    telegram_sent_at: datetime | None = None
    created_at: datetime

class AlertEventResponse(AlertEventBase):
    model_config = ConfigDict(from_attributes=True)