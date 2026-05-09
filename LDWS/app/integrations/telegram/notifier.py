from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db.models import AlertEvent
from app.db.repositories import AreaRepository, StationRepository, AlertEventRepository
from app.integrations.telegram import TelegramBotClient
from app.integrations.telegram import DeliveryStateStore
from app.integrations.telegram import TelegramAlertFormatter
from app.integrations.telegram import TelegramDeliveryRouter

# Định dạng kết quả thông báo
@dataclass
class NotificationResult:
    ok: bool    # Gửi thành công hay thất bại
    event_id: int
    timestamp: str
    chat_id: str | None = None
    error_message: str | None = None


class TelegramAlertNotifier:
    def __init__(self, db: Session):
        self.db = db
        self.alert_event_repo = AlertEventRepository(db)
        self.area_repo = AreaRepository(db)
        self.station_repo = StationRepository(db)

        self.delivery_router = TelegramDeliveryRouter(db)   # Tìm kênh để gửi
        self.bot_client = TelegramBotClient()               # Thực hiện gửi tin
        self.delivery_state_store = DeliveryStateStore()    # Lưu trạng thái vào file JSON
        self.formatter = TelegramAlertFormatter()           # Tạo nội dung tin nhắn HTML
        
    # Hàm gửi 1 sự kiện đơn lẻ
    def send_single_event(self, event: AlertEvent) -> NotificationResult:
        # Tạo khóa thời gian
        event_key_ts = event.timestamp.isoformat()
        current_state = self.delivery_state_store.get(
            event_id=event.event_id,
            timestamp=event_key_ts,
        )

        # Kiểm tra xem tin nhắn này đã được gửi chưa
        if current_state.sent:
            return NotificationResult(
                ok=True,
                event_id=event.event_id,
                timestamp=event_key_ts,
                error_message="Already sent (tracked in file-based delivery state).",
            )
        
        # Tìm kênh Telegram tương ứng với khu vực của sự kiện
        channel = self.delivery_router.resolve_channel_for_event(event)
        if not channel:
            error_message = f"No active Telegram channel found for area_id={event.area_id}"
            
            # Đánh dấu thất bại vào file log JSON
            self.delivery_state_store.mark_failed(
                event_id=event.event_id,
                timestamp=event_key_ts,
                error_message=error_message,
            )
            return NotificationResult(
                ok=False,
                event_id=event.event_id,
                timestamp=event_key_ts,
                error_message=error_message,
            )

        area = self.area_repo.get_by_id(event.area_id)
        station = self.station_repo.get_by_id(event.station_id)

        # Định dạng nội dung tin nhắn HTML
        message_text = self.formatter.format_event(
            event=event,
            area=area,
            station=station,
        )

        # Thực hiện gửi tin nhắn qua Bot Telegram
        send_result = self.bot_client.send_message(
            chat_id=channel.telegram_chat_id,
            text=message_text,
        )

        # Xử lý kết quả trả về từ Bot
        if send_result.ok: # Nếu gửi thành công
            self.delivery_state_store.mark_sent(
                event_id=event.event_id,
                timestamp=event_key_ts,
            )
            return NotificationResult(
                ok=True,
                event_id=event.event_id,
                timestamp=event_key_ts,
                chat_id=channel.telegram_chat_id,
            )
        # Nếu gửi thất bại
        self.delivery_state_store.mark_failed(
            event_id=event.event_id,
            timestamp=event_key_ts,
            error_message=send_result.error_message or "Unknown Telegram send error",
        )
        return NotificationResult(
            ok=False,
            event_id=event.event_id,
            timestamp=event_key_ts,
            chat_id=channel.telegram_chat_id,
            error_message=send_result.error_message,
        )

    # Hàm gửi hàng loạt các sự kiện đang chờ
    def send_pending_events(self, *, limit: int = 50) -> list[NotificationResult]:
        # Lấy danh sách các cảnh báo mới nhất từ DB mà hệ thống nghĩ là chưa gửi
        events = self.alert_event_repo.list_recent_unsent_candidates(limit=limit)
        results: list[NotificationResult] = []

        # Duyệt qua từng sự kiện và gọi hàm gửi đơn lẻ 
        for event in events:
            results.append(self.send_single_event(event))

        return results