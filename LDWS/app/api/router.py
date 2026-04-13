from fastapi import APIRouter # Tạo Router tổng gom nhiều router lại

from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router

api_router = APIRouter(prefix="/api") # Tạo root Router gom tất cả các router con
api_router.include_router(health_router) # Gắn router con (health_router) vào router chính
api_router.include_router(auth_router) # Gắn auth router vào router chính