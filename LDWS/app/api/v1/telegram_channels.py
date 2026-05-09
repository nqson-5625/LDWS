from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_super_admin
from app.db.session import get_db

from app.schemas.common import MessageResponse
from app.schemas.telegram_channel import TelegramChannelCreate, TelegramChannelResponse, TelegramChannelUpdate
from app.services.telegram_channels_service import TelegramChannelService

router = APIRouter(
    prefix="/v1/telegram-channels", 
    tags=["telegram_channels"],
    dependencies=[Depends(get_current_super_admin)]
)

# API lấy danh sách tất cả các kênh telegram
@router.get("/", response_model=list[TelegramChannelResponse])
def list_telegram_channels(
    db: Session = Depends(get_db)
):
    return TelegramChannelService(db).list_telegram_channels()

# API lấy thông tin 1 kênh telegram
@router.get("/{channel_id}", response_model=TelegramChannelResponse)
def get_telegram_channel(
    channel_id: int,
    db: Session = Depends(get_db)
):
    return TelegramChannelService(db).get_telegram_channel(channel_id)

# API tạo 1 kênh telegram mới
@router.post("/", response_model=TelegramChannelResponse)
def create_telegram_channel(
    payload: TelegramChannelCreate,
    db: Session = Depends(get_db)
):
    return TelegramChannelService(db).create_telegram_channel(payload)

# API cập nhật 1 kênh telegram
@router.put("/{channel_id}", response_model=TelegramChannelResponse)
def update_telegram_channel(
    channel_id: int,
    payload: TelegramChannelUpdate,
    db: Session = Depends(get_db)
):
    return TelegramChannelService(db).update_telegram_channel(channel_id, payload)

# API xóa 1 kênh telegram
@router.delete("/{channel_id}", response_model=MessageResponse)
def delete_telegram_channel(
    channel_id: int,
    db: Session = Depends(get_db)
):
    TelegramChannelService(db).delete_telegram_channel(channel_id)
    return MessageResponse(message="Telegram channel deleted successfully")