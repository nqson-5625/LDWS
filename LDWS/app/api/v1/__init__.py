from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router

from app.api.v1.areas import router as areas_router
from app.api.v1.stations import router as stations_router
from app.api.v1.sensor_types import router as sensor_types_router
from app.api.v1.alert_levels import router as alert_levels_router
from app.api.v1.telegram_channels import router as telegram_channels_router
from app.api.v1.sensors import router as sensors_router
from app.api.v1.users import router as users_router
from app.api.v1.sensor_readings import router as sensor_readings_router
from app.api.v1.derived_features import router as derived_features_router
from app.api.v1.alert_events import router as alert_events_router
from app.api.v1.alert_status import router as alert_status_router
from app.api.v1.dashboard import router as dashboard_router
