from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.repositories import AlertLevelRepository
from app.schemas.alert_level import AlertLevelCreate, AlertLevelUpdate

class AlertLevelService:
    def __init__(self, db: Session):
        self.db = db
        self.alert_level_repo = AlertLevelRepository(db)

    def list_alert_levels(self):
        return self.alert_level_repo.list_all()

    def get_alert_level(self, alert_level: int):
        alert_level_obj = self.alert_level_repo.get_by_level(alert_level)
        if not alert_level_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert level not found"
            )
        return alert_level_obj
    
    def create_alert_level(self, payload: AlertLevelCreate):
        existing_by_level = self.alert_level_repo.get_by_level(payload.alert_level)
        if existing_by_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Alert level already exists"
            )
        
        existing_by_name = self.alert_level_repo.get_by_name(payload.alert_name)
        if existing_by_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Alert level name already exists"
            )
        
        return self.alert_level_repo.create(**payload.model_dump())
    
    def update_alert_level(self, alert_level: int, payload: AlertLevelUpdate):
        alert_level_obj = self.get_alert_level(alert_level)

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return alert_level_obj
        
        # Nếu client cập nhật tên cảnh báo
        new_alert_name = update_data.get("alert_name")
        if new_alert_name and new_alert_name != alert_level_obj.alert_name:
            existing_by_name = self.alert_level_repo.get_by_name(new_alert_name)
            if existing_by_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Alert level name already exists"
                )
        
        return self.alert_level_repo.update(alert_level_obj, **update_data)
    
    def delete_alert_level(self, alert_level: int) -> None:
        alert_level_obj = self.get_alert_level(alert_level)
        self.alert_level_repo.delete(alert_level_obj)