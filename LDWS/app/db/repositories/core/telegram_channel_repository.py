from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import TelegramChannel

class TelegramChannelRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, channel_id: int) -> TelegramChannel | None:
        stmt = select(TelegramChannel).where(TelegramChannel.channel_id == channel_id)
        return self.db.execute(stmt).scalar_one_or_none()
    
    # Lấy TelegramChannel theo Area ID
    def get_by_area_id(self, area_id: int) -> TelegramChannel | None:
        stmt = select(TelegramChannel).where(TelegramChannel.area_id == area_id)
        return self.db.execute(stmt).scalar_one_or_none()

    # Lấy TelegramChannel đang hoạt động theo Area ID
    def get_active_by_area_id(self, area_id: int) -> TelegramChannel | None:
        stmt = select(TelegramChannel).where(
            TelegramChannel.area_id == area_id,
            TelegramChannel.is_active.is_(True),
        )
        return self.db.execute(stmt).scalar_one_or_none()

    # Lấy TelegramChannel theo chat_id (do Bot tạo ra)
    def get_by_chat_id(self, telegram_chat_id: str) -> TelegramChannel | None:
        stmt = select(TelegramChannel).where(TelegramChannel.telegram_chat_id == telegram_chat_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_all(self) -> list[TelegramChannel]:
        stmt = select(TelegramChannel).order_by(TelegramChannel.channel_id.asc())
        return list(self.db.execute(stmt).scalars().all())
    
    def create(self, **kwargs) -> TelegramChannel:
        channel = TelegramChannel(**kwargs)
        try:
            self.db.add(channel)
            self.db.flush()
            self.db.refresh(channel)
            self.db.commit()
            return channel
        except Exception:
            self.db.rollback()
            raise

    # Tạo area -> telegram_channel trong cùng 1 transaction ở service    
    def create_in_tx(self, **kwargs) -> TelegramChannel:
        channel = TelegramChannel(**kwargs)
        self.db.add(channel)
        self.db.flush()
        self.db.refresh(channel)
        return channel

    def update(self, channel: TelegramChannel, **kwargs) -> TelegramChannel:
        try:
            for key, value in kwargs.items():
                setattr(channel, key, value)
            self.db.add(channel)
            self.db.flush()
            self.db.refresh(channel)
            self.db.commit()
            return channel
        except Exception:
            self.db.rollback()
            raise

    def delete(self, channel: TelegramChannel) -> None:
        try:
            self.db.delete(channel)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise