from sqlalchemy.orm import Session

from app.db.repositories import AlertEventRepository
from app.integrations.telegram import TelegramAlertNotifier


class TelegramDeliveryService:
    def __init__(self, db: Session):
        self.db = db
        self.alert_event_repo = AlertEventRepository(db)
        self.notifier = TelegramAlertNotifier(db)

    # Phương thức gửi một sự kiện cụ thể khi biết ID và mốc thời gian
    def send_event(self, *, event_id: int, timestamp):
        event = self.alert_event_repo.get_by_pk(event_id, timestamp)
        if not event:
            raise ValueError("Alert event not found")
        return self.notifier.send_single_event(event)

    # Phương thức gửi hàng loạt các sự kiện chưa được xử lý
    def send_pending_events(self, *, limit: int = 50):
        return self.notifier.send_pending_events(limit=limit)