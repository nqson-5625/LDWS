from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_super_admin
from app.db.session import get_db

from app.schemas.common import MessageResponse
from app.schemas.sensor_type import SensorTypeCreate, SensorTypeResponse, SensorTypeUpdate
from app.services.sensor_type_service import SensorTypeService

router = APIRouter(
    prefix="/v1/sensor-types",
    tags=["sensor_types"],
    dependencies=[Depends(get_current_super_admin)]
)

# API lấy tất cả các loại cảm biến
@router.get("/", response_model=list[SensorTypeResponse])
def list_sensor_types(
    db: Session = Depends(get_db)
):
    return SensorTypeService(db).list_sensor_types()

# API lấy thông tin 1 loại cảm biến
@router.get("/{type_code}", response_model=SensorTypeResponse)
def get_sensor_type(
    type_code: str,
    db: Session = Depends(get_db)
):
    return SensorTypeService(db).get_sensor_type(type_code)

# API tạo 1 loại cảm biến mới
@router.post("/", response_model=SensorTypeResponse)
def create_sensor_type(
    payload: SensorTypeCreate,
    db: Session = Depends(get_db)
):
    return SensorTypeService(db).create_sensor_type(payload)

# API cập nhật loại cảm biến
@router.put("/{type_code}", response_model=SensorTypeResponse)
def update_sensor_type(
    type_code: str,
    payload: SensorTypeUpdate,
    db: Session = Depends(get_db)
):
    return SensorTypeService(db).update_sensor_type(type_code, payload)

# API xóa loại cảm biến
@router.delete("/{type_code}", response_model=MessageResponse)
def delete_sensor_type(
    type_code: str,
    db: Session = Depends(get_db)
):
    SensorTypeService(db).delete_sensor_type(type_code)
    return MessageResponse(message="Sensor type deleted successfully")