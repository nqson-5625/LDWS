import argparse
import logging
import time
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.enums import AlertEventType
from app.db.models import DerivedFeature
from app.db.repositories import AlertEventRepository, AlertStatusRepository, DerivedFeatureRepository, StationRepository

from app.db.session import SessionLocal
from app.integrations.telegram import TelegramAlertNotifier
from app.services.alert.alert_rules import assess

log = logging.getLogger(__name__)

AREA_ID_HANOI = 4

_LEVEL_NAMES = {1: "Binh thuong", 2: "Theo doi", 3: "Canh bao", 4: "Nguy hiem", 5: "Rat nguy hiem",}

# Xử lý một trạm: đánh giá mức cảnh báo, tạo event nếu có thay đổi và gửi thông báo
def _process_station(db: Session, feat: DerivedFeature, station_name: str) -> None:
    event_repo  = AlertEventRepository(db)
    status_repo = AlertStatusRepository(db)
    derived_repo = DerivedFeatureRepository(db)

    result        = assess(feat)
    current_level = status_repo.get_current_alert_level(feat.station_id)

    # Giả lập anomaly_score và anomaly_flag
    feat.anomaly_score = 0.0
    feat.anomaly_flag = False
    feat.risk_score = result.risk_score
    feat.alert_level_candidate = result.alert_level

    # Lưu dữ liệu xuống bảng DERIVED_FEATURES
    try:
        derived_repo.upsert(feat)
        db.commit()
    except Exception:
        db.rollback()
        log.exception("Failed to upsert derived feature for station_id=%d", feat.station_id)

    # Xac dinh loai event: CREATED, UPGRADED, DOWNGRADED, RESOLVED
    if current_level is None:
        event_type = AlertEventType.CREATED
    elif result.alert_level > current_level:
        event_type = AlertEventType.UPGRADED
    elif result.alert_level < current_level:
        event_type = AlertEventType.RESOLVED if result.alert_level == 1 else AlertEventType.DOWNGRADED
    else:
        log.info("station=%s level=%d unchanged", station_name, result.alert_level)
        return

    log.info(
        "station=%s level=%d risk=%.2f %s",
        station_name, result.alert_level, result.risk_score, event_type.value,
    )

    rules_str = ("\n  - " + "\n  - ".join(result.violated_rules)) if result.violated_rules else "Khong co vi pham"
    message   = (
        f"[{event_type.value.upper()}] Muc {result.alert_level} — {_LEVEL_NAMES[result.alert_level]}\n"
        f"Risk score: {result.risk_score:.2%}\n"
        f"Vi pham nguong:{rules_str}"
    )
    now     = datetime.now(tz=timezone.utc)
    next_id = event_repo.get_max_event_id() + 1

    try:
        event = event_repo.create(
            event_id=next_id, timestamp=now,
            area_id=feat.area_id, station_id=feat.station_id,
            alert_level=result.alert_level, risk_score=result.risk_score,
            trigger_feature_id=feat.feature_id, trigger_feature_timestamp=feat.timestamp,
            alert_message=message, event_type=event_type.value,
        )
        status_repo.upsert(station_id=feat.station_id, event_id=next_id, event_timestamp=now)
        db.commit()
        log.info("event_id=%d created", next_id)
    except Exception:
        db.rollback()
        log.exception("Failed to create event for station_id=%d", feat.station_id)
        return

    # Gửi Telegram qua notifier 
    result_tg = TelegramAlertNotifier(db).send_single_event(event)
    if not result_tg.ok:
        log.error("Telegram failed — station_id=%d: %s", feat.station_id, result_tg.error_message)


# Chạy pipeline một lần: lấy đặc trưng dẫn xuất mới nhất của tất cả các trạm trong khu vực, đánh giá và tạo event nếu cần
def run_once() -> None:
    db: Session = SessionLocal()
    try:
        # Truy vấn trực tiếp từ view
        query = text("""
            SELECT DISTINCT ON (station_id) * FROM vw_derived_features 
            WHERE "timestamp" >= NOW() - INTERVAL '10 minutes'
            AND area_id = :area_id
            ORDER BY station_id, "timestamp" DESC;
        """)
        result = db.execute(query, {"area_id": AREA_ID_HANOI})
        
        # Ánh xạ dữ liệu động từ View thành các Object model để tái sử dụng toàn diện Rule Engine
        features = []
        for index, row in enumerate(result.mappings()):
            feat = DerivedFeature(
                feature_id=index + 1,  # Khởi tạo ID tạm thời cho luồng xử lý bộ nhớ
                timestamp=row["timestamp"],
                area_id=row["area_id"],
                station_id=row["station_id"],

                rain_1h=row["rain_1h"], rain_3h=row["rain_3h"], 
                rain_24h=row["rain_24h"], rain_3d=row["rain_3d"],
                rain_intensity=row["rain_intensity"],

                tilt_value=row["tilt_value"], tilt_rate=row["tilt_rate"],
                tilt_change_1h=row["tilt_rate"],  
                tilt_change_24h=row["tilt_change_24h"],

                disp_value=row["disp_value"], disp_rate=row["disp_rate"],
                disp_change_1h=row["disp_rate"],
                disp_change_24h=row["disp_change_24h"],

                vibration_value=row["vibration_value"],
                vibration_peak=row["vibration_peak"],
                vibration_flag=row["vibration_flag"],

                temperature_value=row["temperature_value"],
                temperature_flag=row["temperature_flag"]
            )
            features.append(feat)
        if not features:
            log.warning("Khong co derived_features cho area_id=%d", AREA_ID_HANOI)
            return

        for feat in features:
            station = StationRepository(db).get_by_id(feat.station_id)
            if not station:
                log.warning("Khong tim thay station_id=%d", feat.station_id)
                continue
            try:
                _process_station(db, feat, station.station_name)
            except Exception:
                log.exception("Unexpected error — station_id=%d skipped", feat.station_id)
    finally:
        db.close()


# Chạy pipeline liên tục theo khoảng thời gian định sẵn (mặc định 60s)
def run_realtime(interval: int = 60) -> None:
    log.info("Alert pipeline realtime interval=%ds — Ctrl+C de dung", interval)
    while True:
        try:
            run_once()
        except Exception:
            log.exception("Pipeline error — retry next interval")
        time.sleep(interval)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--realtime", action="store_true")
    parser.add_argument("--interval", type=int, default=60)
    args = parser.parse_args()
    run_realtime(args.interval) if args.realtime else run_once()