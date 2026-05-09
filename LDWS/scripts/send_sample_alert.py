import argparse
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.enums import AlertEventType
from app.db.models import AlertEvent, AlertLevel, Area, Station
from app.db.session import SessionLocal
from app.integrations.telegram.notifier import TelegramAlertNotifier

# Lấy ID tiếp theo cho sự kiện mới
def next_event_id(db: Session) -> int:
    value = db.query(func.max(AlertEvent.event_id)).scalar()
    return int(value or 0) + 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--area-id", type=int, required=True)
    parser.add_argument("--station-id", type=int, required=True)
    parser.add_argument("--alert-level", type=int, default=3)
    parser.add_argument("--risk-score", type=float, default=0.87)
    parser.add_argument("--message", default="Cảnh báo mẫu từ script.")
    args = parser.parse_args()

    db: Session = SessionLocal()
    try:
        area = db.query(Area).filter(Area.area_id == args.area_id).one_or_none()
        if not area:
            raise ValueError("Area not found")

        station = db.query(Station).filter(Station.station_id == args.station_id).one_or_none()
        if not station:
            raise ValueError("Station not found")

        level = db.query(AlertLevel).filter(AlertLevel.alert_level == args.alert_level).one_or_none()
        if not level:
            raise ValueError("Alert level not found")

        now = datetime.now(timezone.utc)
        event = AlertEvent(
            event_id=next_event_id(db),
            timestamp=now,
            area_id=area.area_id,
            station_id=station.station_id,
            alert_level=level.alert_level,
            risk_score=args.risk_score,
            alert_message=args.message,
            event_type=AlertEventType.CREATED,
            telegram_sent=False,
        )
        db.add(event)
        db.commit()       # Xác nhận lưu thay đổi
        db.refresh(event) # Cập nhật lại thông tin object sau khi lưu

        # Thực hiện gửi Telegram
        notifier = TelegramAlertNotifier(db)
        result = notifier.send_single_event(event)
        print(result)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

# uv run python -m scripts.send_sample_alert --area-id 1 --station-id 35
if __name__ == "__main__":
    main()