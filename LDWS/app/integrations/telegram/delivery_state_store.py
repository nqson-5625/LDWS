import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings

# Định nghĩa cấu trúc trạng thái của một lần gửi tin nhắn
@dataclass
class DeliveryState:
    sent: bool = False
    sent_at: str | None = None
    retry_count: int = 0 # Số lần đã thử gửi lại
    last_error: str | None = None # Nội dung lỗi của lần thử gần nhất
    last_attempt_at: str | None = None # Thời điểm thực hiện lần thử gần nhất

# Đọc/ghi trạng thái vào file JSON
class DeliveryStateStore:
    def __init__(self, path: str | None = None):
        # Xác định đường dẫn file
        self.path = Path(path or settings.telegram_delivery_state_file)
        # Tạo các thư mục cha nếu chúng chưa tồn tại
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Nếu file chưa tồn tại, tạo file mới với nội dung là một dict rỗng
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")
        
    # Đọc toàn bộ nội dung file JSON vào bộ nhớ
    def _load_all(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8"))

    # Lưu toàn bộ dict vào file JSON
    def _save_all(self, data: dict) -> None:
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # Tạo ra một khóa sự kiện duy nhất 
    # VD: "101__2026-05-07T14:00:00"
    def _event_key(self, *, event_id: int, timestamp: str) -> str:
        return f"{event_id}__{timestamp}"

    # Lấy trạng thái gửi của một sự kiện cụ thể
    def get(self, *, event_id: int, timestamp: str) -> DeliveryState:
        data = self._load_all()
        raw = data.get(self._event_key(event_id=event_id, timestamp=timestamp), {})
        return DeliveryState(**raw)

    # Đánh dấu sự kiện đã gửi thành công
    def mark_sent(self, *, event_id: int, timestamp: str) -> None:
        data = self._load_all()
        key = self._event_key(event_id=event_id, timestamp=timestamp)

        current = data.get(key, {})
        current["sent"] = True  # Chuyển trạng thái thành True
        current["sent_at"] = datetime.now(timezone.utc).isoformat()
        current["last_error"] = None    # Xóa lỗi cũ nếu có
        current["last_attempt_at"] = datetime.now(timezone.utc).isoformat()

        data[key] = current
        self._save_all(data)# Lưu lại vào file

    # Đánh dấu lần gửi bị thất bại
    def mark_failed(self, *, event_id: int, timestamp: str, error_message: str) -> None:
        data = self._load_all()
        key = self._event_key(event_id=event_id, timestamp=timestamp)

        current = data.get(key, {})
        current["sent"] = False  # Chuyển trạng thái thành False
        current["retry_count"] = int(current.get("retry_count", 0)) + 1   # Tăng số lần thử lại lên 1
        current["last_error"] = error_message[:2000]   # Giới hạn nội dung lỗi tối đa 2000 ký tự
        current["last_attempt_at"] = datetime.now(timezone.utc).isoformat()

        data[key] = current
        self._save_all(data)