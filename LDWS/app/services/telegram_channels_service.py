from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.repositories import AreaRepository, TelegramChannelRepository
from app.schemas.telegram_channel import TelegramChannelCreate, TelegramChannelUpdate

class TelegramChannelService:
    def __init__(self, db: Session):
        self.db = db
        self.area_repo = AreaRepository(db)
        self.channel_repo = TelegramChannelRepository(db)

    def list_telegram_channels(self):
        return self.channel_repo.list_all()
    
    def get_telegram_channel(self, channel_id: int):
        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Telegram channel not found"
            )
        return channel
        
    def create_telegram_channel(self, payload: TelegramChannelCreate):
        area = self.area_repo.get_by_id(payload.area_id)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Area does not exist"
            )
            
        # 1 area có tối đa 1 channel
        existing_by_area = self.channel_repo.get_by_area_id(payload.area_id)
        if existing_by_area:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This area already has a telegram channel"
            )
            
        # 1 group chat chỉ phục vụ 1 khu vực
        existing_by_chat_id = self.channel_repo.get_by_chat_id(payload.telegram_chat_id)
        if existing_by_chat_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Telegram chat id already exists"
            )
            
        return self.channel_repo.create(**payload.model_dump())
    
    def update_telegram_channel(self, channel_id: int, payload: TelegramChannelUpdate):
        channel = self.get_telegram_channel( channel_id)

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return channel
        
        # Lấy area_id, chat_id client yêu cầu update (nếu có)
        target_area_id = update_data.get("area_id", channel.area_id)
        target_chat_id = update_data.get("telegram_chat_id", channel.telegram_chat_id)

        area = self.area_repo.get_by_id(target_area_id)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Area does not exist"
            )
        
        # area đích có 1 kênh telegram nhưng không phải nó (khác channel_id)
        existing_by_area = self.channel_repo.get_by_area_id(target_area_id)
        if existing_by_area and existing_by_area.channel_id != channel.channel_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This area already has a telegram channel"
            )
        
        # chat_id đích trùng với 1 channel khác (khác channel_id)
        exisitng_by_chat_id = self.channel_repo.get_by_chat_id(target_chat_id)
        if exisitng_by_chat_id and exisitng_by_chat_id.channel_id != channel.channel_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Telegram chat id already exists"
            )
        
        return self.channel_repo.update(channel, **update_data)
    
    def delete_telegram_channel(self, channel_id: int) -> None:
        channel = self.get_telegram_channel(channel_id)
        self.channel_repo.delete(channel)