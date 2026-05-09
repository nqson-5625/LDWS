from pydantic import BaseModel, ConfigDict


class AlertLevelBase(BaseModel):
    alert_name: str
    alert_color: str
    description: str | None = None


class AlertLevelCreate(AlertLevelBase):
    alert_level: int


class AlertLevelUpdate(BaseModel):
    alert_name: str | None = None
    alert_color: str | None = None
    description: str | None = None


class AlertLevelResponse(AlertLevelBase):
    alert_level: int

    model_config = ConfigDict(from_attributes=True)