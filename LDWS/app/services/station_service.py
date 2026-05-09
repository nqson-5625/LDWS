from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.repositories import AreaRepository, StationRepository
from app.schemas.station import StationCreate, StationUpdate

class StationService:
    def __init__(self, db: Session):
        self.db = db
        self.area_repo = AreaRepository(db)
        self.station_repo = StationRepository(db)

    def list_station(self):
        return self.station_repo.list_all()
    
    def get_station(self, station_id: int):
        station = self.station_repo.get_by_id(station_id)
        if not station:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Station not found"
            )
        return station
    
    def create_station(self, payload: StationCreate):
        area = self.area_repo.get_by_id(payload.area_id)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Area does not exist"
            )
        
        existing_station = self.station_repo.get_by_area_and_name(
            payload.area_id,
            payload.station_name
        )

        if existing_station:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Station name already exists in this area"
            )
        
        return self.station_repo.create(**payload.model_dump())
    
    def update_station(self, station_id: int, payload: StationUpdate):
        station = self.get_station(station_id)

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return station
        
        # Lấy area_id và station_name được client yêu cầu cập nhật, nếu không có thì dùng giá trị hiện tại trong station
        target_area_id = update_data.get("area_id", station.area_id)
        target_station_name = update_data.get("station_name", station.station_name)

        area = self.area_repo.get_by_id(target_area_id)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Area does not exist"
            )
        
        # Kiểm tra xem tại target_area có tồn tại Station trùng tên mới cập nhật không
        existing_station = self.station_repo.get_by_area_and_name(
            target_area_id,
            target_station_name
        )

        # Nếu tồn tại station trùng tên tại target area mà không phải nó (khác ID)
        if existing_station and existing_station.station_id != station.station_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Station name already exists in this area"
            )
        
        return self.station_repo.update(station, **update_data)
    
    def delete_station(self, station_id: int) -> None:
        station = self.get_station(station_id)
        self.station_repo.delete(station)