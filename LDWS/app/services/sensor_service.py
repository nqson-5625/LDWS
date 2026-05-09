from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.db.repositories import SensorRepository, SensorTypeRepository, StationRepository
from app.permissions.station_scope import ensure_station_scope
from app.schemas.sensor import SensorCreate, SensorStatusUpdate, SensorUpdate

class SensorService:
    def __init__(self, db: Session):
        self.db = db
        self.sensor_repo = SensorRepository(db)
        self.station_repo = StationRepository(db)
        self.sensor_type_repo = SensorTypeRepository(db)

    # Phân quyền view
    def list_sensors(self, current_user):
        if current_user.role == UserRole.SUPER_ADMIN:
            return self.sensor_repo.list_all()
        
        if current_user.role == UserRole.STATION_ADMIN:
            return self.sensor_repo.list_by_station(current_user.station_id)
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view sensors"
        )
    
    def get_sensor(self, sensor_id: int, current_user):
        sensor = self.sensor_repo.get_by_id(sensor_id)
        if not sensor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sensor not found"
            )
        
        # Chống IDOR, station_admin_1 không được lấy dữ liệu của station_2
        ensure_station_scope(current_user, sensor.station_id)
        return sensor
    
    def create_sensor(self, payload: SensorCreate, current_user):
        station_id = payload.station_id

        # Đảm bảo station_admin không nhập station_id của trạm khác
        if current_user.role == UserRole.STATION_ADMIN:
            station_id = current_user.station_id

        if station_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="station_id is required"
            )
        
        # Station tồn tại
        station = self.station_repo.get_by_id(station_id)
        if not station:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Station does not exist"
            )
        
        # Loại cảm biến tồn tại
        sensor_type = self.sensor_type_repo.get_by_code(payload.type_code)
        if not sensor_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sensor type does not exist"
            )
        
        # Nếu user nhập mã phần cứng (sensor_code), đảm bảo không bị trùng
        if payload.sensor_code:
            existing_sensor = self.sensor_repo.get_by_sensor_code(payload.sensor_code)
            if existing_sensor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sensor code already exists"
                )
            
        ensure_station_scope(current_user, station_id)
        create_data = payload.model_dump()
        create_data["station_id"] = station_id # Chèn lại đúng station_id đã được phân quyền

        return self.sensor_repo.create(**create_data)
    
    def update_sensor(self, sensor_id: int, payload: SensorUpdate, current_user):
        sensor = self.get_sensor(sensor_id, current_user) # get_sensor() đã check quyền

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return sensor
        
        # Chống leo thang đặc quyền: Không cho station_admin chuyển sensor sang station khác
        if current_user.role == UserRole.STATION_ADMIN and "station_id" in update_data:
            update_data.pop("station_id") # Xóa, không cho cập nhật station_id

        target_station_id = update_data.get("station_id", sensor.station_id)
        target_type_code = update_data.get("type_code", sensor.type_code)
        target_sensor_code = update_data.get("sensor_code", sensor.sensor_code)

        # Kiểm tra station tồn tại
        station = self.station_repo.get_by_id(target_station_id)
        if not station:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Station does not exist"
            )
        
        # Kiểm tra sensor_type tồn tại
        sensor_type = self.sensor_type_repo.get_by_code(target_type_code)
        if not sensor_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Sensor type does not exist"
            )

        # Kiểm tra trùng lặp mã phần cứng (sensor_code)
        if target_sensor_code:
            existing_sensor = self.sensor_repo.get_by_sensor_code(target_sensor_code)
            if existing_sensor and existing_sensor.sensor_id != sensor.sensor_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Sensor code already exists"
                )
            
        # Đảm bảo user (SUPER_ADMIN hoặc STATION_ADMIN) có quyền trên cả trạm cũ và trạm mới
        ensure_station_scope(current_user, sensor.station_id)
        ensure_station_scope(current_user, target_station_id)

        return self.sensor_repo.update(sensor, **update_data)
    
    def update_sensor_status(self, sensor_id: int, payload: SensorStatusUpdate, current_user):
        sensor = self.get_sensor(sensor_id, current_user)
        ensure_station_scope(current_user, sensor.station_id)
        return self.sensor_repo.update(sensor, status=payload.status)
    
    # Cấm không được xóa sensor vật lý
    def delete_sensor(self, sensor_id: int, current_user) -> None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System strictly prohibits deleting physical sensors. Please deactivate it instead.",
        )