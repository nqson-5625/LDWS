from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db

from app.schemas.common import MessageResponse
from app.schemas.sensor import SensorCreate, SensorResponse, SensorStatusUpdate, SensorUpdate
from app.services.sensor_service import SensorService

router = APIRouter(prefix="/v1/sensors", tags=["sensors"])

# API lấy danh sách tất cả các sensors (đối với super_admin)
# hoặc lấy danh sách tất cả các sensors của trạm mình (đối với station_admin)
@router.get("/", response_model=list[SensorResponse])
def list_sensors(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return SensorService(db).list_sensors(current_user)

# API lấy thông tin của 1 sensors cụ thể
@router.get("/{sensor_id}", response_model=SensorResponse)
def get_sensor(
    sensor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return SensorService(db).get_sensor(sensor_id, current_user)

# API để super_admin (hoặc station_admin) tạo 1 sensor mới
@router.post("/", response_model=SensorResponse)
def create_sensor(
    payload: SensorCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return SensorService(db).create_sensor(payload, current_user)

# API để super_admin (hoặc station_admin) cập nhật 1 sensor
@router.put("/{sensor_id}", response_model=SensorResponse)
def update_sensor(
    sensor_id: int,
    payload: SensorUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return SensorService(db).update_sensor(sensor_id, payload, current_user)

# API để super_admin (hoặc station_admin) cập nhật trạng thái sensor
@router.patch("/{sensor_id}/status", response_model=SensorResponse)
def update_sensor_status(
    sensor_id: int,
    payload: SensorStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return SensorService(db).update_sensor_status(sensor_id, payload, current_user)

# API để xóa sensor (bị chặn ở tầng Service và DB)
@router.delete("/{sensor_id}", response_model=MessageResponse)
def delete_sensor(
    sensor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    SensorService(db).delete_sensor(sensor_id, current_user)
    return MessageResponse(message="Sensor deleted successfully")