from fastapi import APIRouter # Tạo Router tổng gom nhiều router lại

from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router

from app.api.v1 import (
    users_router,
    areas_router, stations_router,
    sensor_types_router, sensors_router,
    alert_levels_router, telegram_channels_router,
    sensor_readings_router, derived_features_router,
    alert_events_router, alert_status_router,
    dashboard_router
)

api_router = APIRouter(prefix="/api") # Tạo root Router gom tất cả các router con
api_router.include_router(health_router) # Gắn router con (health_router) vào router chính
api_router.include_router(auth_router) # Gắn auth router vào router chính

api_router.include_router(users_router)
api_router.include_router(areas_router)
api_router.include_router(stations_router)
api_router.include_router(sensor_types_router)
api_router.include_router(alert_levels_router)
api_router.include_router(telegram_channels_router)
api_router.include_router(sensors_router)

api_router.include_router(sensor_readings_router)
api_router.include_router(derived_features_router)
api_router.include_router(alert_events_router)
api_router.include_router(alert_status_router)
api_router.include_router(dashboard_router)