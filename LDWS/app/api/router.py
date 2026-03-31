from fastapi import APIRouter # Tạo Router tổng gom nhiều router lại
from app.api.v1.health import router as health_router

api_router = APIRouter() # Tạo root Router gom tất cả các router con
api_router.include_router(health_router) # Gắn router con (health_router) vào router chính