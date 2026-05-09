from dataclasses import dataclass

import httpx

from app.core.config import settings

# Lưu kết quả trả về sau mỗi lần gửi tin nhắn
@dataclass
class TelegramSendResult:
    ok: bool
    telegram_message_id: int | None = None
    raw_response: dict | None = None
    error_message: str | None = None

# Logic gửi tin nhắn
class TelegramBotClient:
    def __init__(self):
        self.enabled = settings.telegram_enabled
        self.bot_token = settings.telegram_bot_token
        self.api_base_url = settings.telegram_api_base_url.rstrip("/") # đảm bảo URL không bị dư dấu gạch chéo ở cuối
        self.parse_mode = settings.telegram_parse_mode
        self.disable_notification = settings.telegram_disable_notification

    # Hàm nội bộ để xây dựng URL gọi API theo cấu trúc của Telegram
    def _build_url(self, method: str) -> str:
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is not configured")
        
        # Cấu trúc chuẩn: https://api.telegram.org/bot<token>/<method>
        return f"{self.api_base_url}/bot{self.bot_token}/{method}"
    

    # Phương thức gửi tin nhắn
    def send_message(self, *, chat_id: str, text: str) -> TelegramSendResult:
        # Kiểm tra có cho phép tích hợp Telegram không
        if not self.enabled:
            return TelegramSendResult(
                ok=False,
                error_message="Telegram integration is disabled (TELEGRAM_ENABLED=false).",
            )

        try:
            # Chuẩn bị URL và Payload gửi đi
            url = self._build_url("sendMessage")
            payload = {
                "chat_id": chat_id,             # ID kênh chat
                "text": text,                   # Nội dung tin nhắn
                "parse_mode": self.parse_mode,  # Định dạng HTML hoặc Markdown
                "disable_notification": self.disable_notification, # Gửi im lặng hay không
            }

            # Thực hiện gọi HTTP POST tới Telegram
            with httpx.Client(timeout=30.0) as client: # timeout=30.0 để tránh treo ứng dụng nếu mạng Telegram chậm
                response = client.post(url, json=payload)
                response.raise_for_status() # Tự động ném lỗi nếu HTTP Status Code >= 400 (ví dụ: 404, 500)
                data = response.json() # Giải mã kết quả JSON trả về

            # Kiểm tra phản hồi logic từ Telegram
            if not data.get("ok"):
                return TelegramSendResult(
                    ok=False,
                    raw_response=data,
                    error_message=str(data),
                )

            # Thành công - Trích xuất thông tin tin nhắn
            result_data = data.get("result", {})
            return TelegramSendResult(
                ok=True,
                telegram_message_id=result_data.get("message_id"),
                raw_response=data,
            )
            
        except Exception as exc:
            # Xử lý các lỗi ngoại lệ 
            return TelegramSendResult(
                ok=False,
                error_message=str(exc),
            )