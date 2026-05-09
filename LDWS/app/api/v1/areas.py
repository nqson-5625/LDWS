from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_super_admin
from app.db.session import get_db

from app.schemas.area import AreaCreate, AreaResponse, AreaUpdate
from app.schemas.common import MessageResponse

from app.services.area_service import AreaService

router = APIRouter(
    prefix="/v1/areas", 
    tags=["areas"],

    # Không cho phép truy cập API khi get_current_super_admin() chưa xác minh xong
    dependencies=[Depends(get_current_super_admin)]
)

# API lấy danh sách areas
@router.get("/", response_model=list[AreaResponse])
def list_areas(
    db: Session = Depends(get_db)
):
    return AreaService(db).list_areas()

# API lấy chi tiết 1 area
@router.get("/{area_id}", response_model=AreaResponse)
def get_area(
    area_id: int, # Bắt {area_id} trên URL, ép sang int
    db: Session = Depends(get_db)
):
    return AreaService(db).get_area(area_id)

# API tạo area mới
@router.post("/", response_model=AreaResponse)
def create_area(
    payload: AreaCreate,
    db: Session = Depends(get_db)
):
    return AreaService(db).create_area(payload)

# API cập nhật area
@router.put("/{area_id}", response_model=AreaResponse)
def update_area(
    area_id: int,
    payload: AreaUpdate,
    db: Session = Depends(get_db)
):
    return AreaService(db).update_area(area_id, payload)

# API xóa area
@router.delete("/{area_id}", response_model=MessageResponse)
def delete_area(
    area_id: int,
    db: Session = Depends(get_db)
):
    AreaService(db).delete_area(area_id)
    return MessageResponse(message="Area deleted successfully")