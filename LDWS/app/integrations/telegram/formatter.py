from app.db.models import AlertEvent, Area, Station

# Định dạng nội dung tin nhắn
class TelegramAlertFormatter:
    @staticmethod
    def format_event(*, event: AlertEvent, area: Area | None = None, station: Station | None = None) -> str:
        area_name = area.area_name if area else f"area_id={event.area_id}"
        station_name = station.station_name if station else f"station_id={event.station_id}"
        risk_text = f"{event.risk_score:.2f}" if event.risk_score is not None else "N/A"
        msg = event.alert_message or "Không có nội dung chi tiết."

        event_type_text = (
            event.event_type.value
            if hasattr(event.event_type, "value")
            else str(event.event_type)
        )

        return (
            "<b>CẢNH BÁO SẠT LỞ !!!</b>\n"
            f"<b>Khu vực:</b> {area_name}\n"
            f"<b>Trạm:</b> {station_name}\n"
            f"<b>Mức cảnh báo:</b> {event.alert_level}\n"
            f"<b>Risk score:</b> {risk_text}\n"
            f"<b>Loại sự kiện:</b> {event_type_text}\n"
            f"<b>Thời điểm:</b> {event.timestamp.isoformat()}\n"
            f"<b>Nội dung:</b> {msg}"
        )