from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.repositories import AreaRepository, TelegramChannelRepository
from app.schemas.area import AreaCreate, AreaUpdate

class AreaService:
    def __init__(self, db: Session):
        self.db = db
        self.area_repo = AreaRepository(db)
        self.telegram_channel_repo = TelegramChannelRepository(db)

    # Tạo channel_name tự động tạm thời
    def _build_auto_channel_name(self, area_name: str) -> str:
        return f"[AUTO] {area_name}"

    # Tạo chat_id tự động tạm thời
    def _build_auto_chat_id(self, area_id: int) -> str:
        return f"AUTO_PENDING_AREA_{area_id}"

    # Đảm bảo 1 area có 1 telegram_channel (Dùng trong Transaction)
    def _ensure_telegram_channel_for_area_in_tx(self, area) -> None:
        # Lấy channel ứng với area
        existing_channel = self.telegram_channel_repo.get_by_area_id(area.area_id)
        if existing_channel:
            return

        self.telegram_channel_repo.create_in_tx(
            area_id=area.area_id,
            channel_name=self._build_auto_channel_name(area.area_name),
            telegram_chat_id=self._build_auto_chat_id(area.area_id),
            channel_link=None,
            qr_code_url=None,
            is_active=False,  # placeholder
        )

    def list_areas(self):
        return self.area_repo.list_all()
    
    def get_area(self, area_id: int):
        area = self.area_repo.get_by_id(area_id)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Area not found"
            )
        return area
    
    def create_area(self, payload: AreaCreate): 
        existing_area = self.area_repo.get_by_name(payload.area_name)
        if existing_area:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Area name already exists"
            )
        
        try:
            # .model_dump() biến payload (Pydantic obj) thành Dict
            # ** để giải nén nhét vào hàm create của Repository
            area = self.area_repo.create_in_tx(**payload.model_dump())

            # Tự động tạo telegram channel placeholder
            self._ensure_telegram_channel_for_area_in_tx(area)

            self.db.commit()
            self.db.refresh(area)

            return area

        except HTTPException:
            self.db.rollback()
            raise
        except Exception as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create area and telegram channel atomically: {str(exc)}"
            )
    
    def update_area(self, area_id: int, payload: AreaUpdate):
        area = self.get_area(area_id)

        # exclude_unset=True => chỉ cập nhật phần mới, các phần cũ giữ nguyên
        update_data = payload.model_dump(exclude_unset=True)

        if not update_data: # Nếu request rỗng
            return area # Trả về user cũ
        
        # Nếu user đổi tên
        new_area_name = update_data.get("area_name")
        if new_area_name and new_area_name != area.area_name:
            existing_area = self.area_repo.get_by_name(new_area_name)
            if existing_area:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Area name already exists"
                )
            
        updated_area = self.area_repo.update(area, **update_data)

        # Nếu channel đang là auto placeholder thì sync tên
        channel = self.telegram_channel_repo.get_by_area_id(updated_area.area_id)
        if channel and channel.channel_name.startswith("[AUTO] "):
            self.telegram_channel_repo.update(
                channel,
                channel_name=self._build_auto_channel_name(updated_area.area_name),
            )

        return updated_area
        
    def delete_area(self, area_id: int) -> None:
        area = self.get_area(area_id)
        self.area_repo.delete(area)