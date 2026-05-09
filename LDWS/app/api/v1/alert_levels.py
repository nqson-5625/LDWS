from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_super_admin
from app.db.session import get_db

from app.schemas.alert_level import AlertLevelCreate, AlertLevelResponse, AlertLevelUpdate
from app.schemas.common import MessageResponse
from app.services.alert_level_service import AlertLevelService

router = APIRouter(
    prefix="/v1/alert-levels",
    tags=["alert_levels"],
    dependencies=[Depends(get_current_super_admin)]
)

# API lấy danh sách tất cả các cấp cảnh báo
@router.get("/", response_model=list[AlertLevelResponse])
def list_alert_levels(
    db: Session = Depends(get_db)
):
    return AlertLevelService(db).list_alert_levels()

# API lấy thông tin 1 cấp cảnh báo
@router.get("/{alert_level}", response_model=AlertLevelResponse)
def get_alert_level(
    alert_level: int,
    db: Session = Depends(get_db)
):
    return AlertLevelService(db).get_alert_level(alert_level)

# API tạo 1 cấp cảnh báo mới
@router.post("/", response_model=AlertLevelResponse)
def create_alert_level(
    payload: AlertLevelCreate,
    db: Session = Depends(get_db)
):
    return AlertLevelService(db).create_alert_level(payload)

# API cập nhật 1 cấp cảnh báo
@router.put("/{alert_level}", response_model=AlertLevelResponse)
def update_alert_level(
    alert_level: int,
    payload: AlertLevelUpdate,
    db: Session = Depends(get_db)
):
    return AlertLevelService(db).update_alert_level(alert_level, payload)

# API xóa 1 cấp cảnh báo
@router.delete("/{alert_level}", response_model=MessageResponse)
def delete_alert_level(
    alert_level: int,
    db: Session = Depends(get_db)
):
    AlertLevelService(db).delete_alert_level(alert_level)
    return MessageResponse(message="Alert level deleted successfully")