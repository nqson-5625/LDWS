from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_super_admin
from app.db.session import get_db

from app.schemas.common import MessageResponse
from app.schemas.station import StationCreate, StationResponse, StationUpdate
from app.services.station_service import StationService

router = APIRouter(
    prefix="/v1/stations", 
    tags=["stations"],
    dependencies=[Depends(get_current_super_admin)]
)

# API lấy danh sách tất cả Stations
@router.get("/", response_model=list[StationResponse])
def list_station(
    db: Session = Depends(get_db)
):
    return StationService(db).list_station()

# API lấy thông tin 1 station
@router.get("/{station_id}", response_model=StationResponse)
def get_station(
    station_id: int,
    db: Session = Depends(get_db)
):
    return StationService(db).get_station(station_id)

# API tạo station mới
@router.post("/", response_model=StationResponse)
def create_station(
    payload: StationCreate,
    db: Session = Depends(get_db)
):
    return StationService(db).create_station(payload)

# API cập nhật Station
@router.put("/{station_id}", response_model=StationResponse)
def update_station(
    station_id: int, 
    payload: StationUpdate,
    db: Session = Depends(get_db)
):
    return StationService(db).update_station(station_id, payload)

# API xóa station
@router.delete("/{station_id}", response_model=MessageResponse)
def delete_station(
    station_id: int,
    db: Session = Depends(get_db)
):
    StationService(db).delete_station(station_id)
    return MessageResponse(message="Station deleted successfully")