from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.repositories import SensorRepository, SensorTypeRepository
from app.schemas.sensor_type import SensorTypeCreate, SensorTypeUpdate

class SensorTypeService:
    def __init__(self, db: Session):
        self.db = db
        self.sensor_type_repo = SensorTypeRepository(db)
        self.sensor_repo = SensorRepository(db)

    def list_sensor_types(self):
        return self.sensor_type_repo.list_all()
    
    def get_sensor_type(self, type_code: str):
        sensor_type = self.sensor_type_repo.get_by_code(type_code)
        if not sensor_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sensor type not found"
            )
        return sensor_type
    
    def create_sensor_type(self, payload: SensorTypeCreate):
        existing_by_code = self.sensor_type_repo.get_by_code(payload.type_code)
        if existing_by_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sensor type code already exists"
            )
        
        existing_by_name = self.sensor_type_repo.get_by_name(payload.type_name)
        if existing_by_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sensor type name already exists"
            )
        
        return self.sensor_type_repo.create(**payload.model_dump())
    
    def update_sensor_type(self, type_code: str, payload: SensorTypeUpdate):
        sensor_type = self.get_sensor_type(type_code)

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return sensor_type
        
        # Nếu client đổi type_name
        new_type_name = update_data.get("type_name")
        if new_type_name and new_type_name != sensor_type.type_name:
            existing_by_name = self.sensor_type_repo.get_by_name(new_type_name)
            if existing_by_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sensor type name already exists"
                )
            
        return self.sensor_type_repo.update(sensor_type, **update_data)
    
    def delete_sensor_type(self, type_code: str) -> None:
        sensor_type = self.get_sensor_type(type_code)

        # Lấy list[Sensor] sử dụng type_code muốn xóa
        sensors_using_type = self.sensor_repo.get_by_type_code(type_code)

        if sensors_using_type: # Nếu tồn tại Sensor đang sử dụng type_code này thì báo lỗi
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete sensor type because it is being used by sensors"
            )
        
        self.sensor_type_repo.delete(sensor_type)


