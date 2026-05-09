from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TelegramChannelBase(BaseModel):
    area_id: int
    channel_name: str
    telegram_chat_id: str
    channel_link: str | None = None
    qr_code_url: str | None = None
    is_active: bool = True


class TelegramChannelCreate(TelegramChannelBase):
    pass


class TelegramChannelUpdate(BaseModel):
    area_id: int | None = None
    channel_name: str | None = None
    telegram_chat_id: str | None = None
    channel_link: str | None = None
    qr_code_url: str | None = None
    is_active: bool | None = None


class TelegramChannelResponse(TelegramChannelBase):
    channel_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)