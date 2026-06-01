from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DerivedFeatureBase(BaseModel):
    area_id: int
    station_id: int

    rain_1h: float | None = None
    rain_3h: float | None = None
    rain_24h: float | None = None
    rain_3d: float | None = None
    rain_intensity: float | None = None

    tilt_value: float | None = None
    tilt_rate: float | None = None
    tilt_change_1h: float | None = None
    tilt_change_24h: float | None = None

    disp_value: float | None = None
    disp_rate: float | None = None
    disp_change_1h: float | None = None
    disp_change_24h: float | None = None

    vibration_value: float | None = None
    vibration_peak: float | None = None
    vibration_flag: bool | None = None

    temperature_value: float | None = None
    temperature_flag: bool | None = None

    anomaly_score: float | None = None
    anomaly_flag: bool = False
    risk_score: float | None = None
    alert_level_candidate: int | None = None


class DerivedFeatureCreate(DerivedFeatureBase):
    feature_id: int
    timestamp: datetime


class DerivedFeatureUpdate(BaseModel):
    area_id: int | None = None
    station_id: int | None = None

    rain_1h: float | None = None
    rain_3h: float | None = None
    rain_24h: float | None = None
    rain_3d: float | None = None
    rain_intensity: float | None = None

    tilt_value: float | None = None
    tilt_rate: float | None = None
    tilt_change_1h: float | None = None
    tilt_change_24h: float | None = None

    disp_value: float | None = None
    disp_rate: float | None = None
    disp_change_1h: float | None = None
    disp_change_24h: float | None = None

    vibration_value: float | None = None
    vibration_peak: float | None = None
    vibration_flag: bool | None = None

    temperature_value: float | None = None
    temperature_flag: bool | None = None

    anomaly_score: float | None = None
    anomaly_flag: bool | None = None
    risk_score: float | None = None
    alert_level_candidate: int | None = None


class DerivedFeatureResponse(DerivedFeatureCreate):
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
