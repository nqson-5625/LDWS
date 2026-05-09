from sqlalchemy.orm import Session

from app.db.models import AlertEvent
from app.db.repositories.core.telegram_channel_repository import TelegramChannelRepository

# Điều hướng: có alert_event => xác định area => xác định telegram_channel
class TelegramDeliveryRouter:
    def __init__(self, db: Session):
        self.db = db
        self.channel_repo = TelegramChannelRepository(db)

    # Tìm kênh phù hợp cho một sự kiện
    def resolve_channel_for_event(self, event: AlertEvent):
        return self.channel_repo.get_active_by_area_id(event.area_id)