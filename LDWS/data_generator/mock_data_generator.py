from __future__ import annotations

import argparse
import logging
import math
import random
import sys
import time
from datetime import datetime, timezone
from sqlalchemy import text
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.db.session import SessionLocal
from app.schemas.sensor_reading import SensorReadingCreate
from app.services.sensor_reading_service import SensorReadingService


# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# Trạng thái nội bộ — mô phỏng quá trình vật lý liên tục
# key = sensor_id
_sensor_state: dict[int, dict] = {}


def _state(sensor_id: int, defaults: dict) -> dict:
    if sensor_id not in _sensor_state:
        _sensor_state[sensor_id] = dict(defaults)
    return _sensor_state[sensor_id]


# Hàm sinh giá trị theo từng loại cảm biến

def _gen_rain(sensor_id: int, ts: datetime) -> tuple:
    # Mô phỏng mưa theo chuỗi Markov đơn giản.
    st = _state(sensor_id, {"active": False, "intensity": 0.0, "remaining": 0})

    if st["active"]:    
        st["remaining"] -= 1
        if st["remaining"] <= 0:
            st["active"] = False
            st["intensity"] = 0.0
        v1 = max(0.0, round(st["intensity"] + random.gauss(0, 0.08), 3))
    else:
        if random.random() < 0.15:          # xác suất bắt đầu mưa
            st["active"] = True
            st["intensity"] = random.uniform(0.05, 2.5)   # mm/phút
            st["remaining"] = random.randint(5, 60)
            v1 = round(st["intensity"], 3)
        else:
            v1 = 0.0

    return v1, None, None


def _gen_tilt(sensor_id: int, ts: datetime) -> tuple:
    rng = random.Random(sensor_id)          # nền cố định riêng từng sensor
    base_x = rng.uniform(-2.0, 2.0)
    base_y = rng.uniform(-1.5, 1.5)

    st = _state(sensor_id, {"x": base_x, "y": base_y})
    st["x"] += random.gauss(0.002, 0.05)
    st["y"] += random.gauss(0.001, 0.04)
    st["x"] = max(-20.0, min(20.0, st["x"]))
    st["y"] = max(-20.0, min(20.0, st["y"]))

    return round(st["x"], 4), round(st["y"], 4), None


def _gen_vibration(sensor_id: int, ts: datetime) -> tuple:
    is_reference = (sensor_id % 2 == 0)
    base = 0.005 if is_reference else 0.012
    noise = 0.003

    event_mag = 0.0
    if not is_reference and random.random() < 0.02:
        event_mag = random.uniform(0.05, 0.20)

    vx = abs(random.gauss(base + event_mag, noise))
    vy = abs(random.gauss(base + event_mag * 0.8, noise))
    vz = abs(random.gauss(base + event_mag * 0.5, noise))

    return round(vx, 5), round(vy, 5), round(vz, 5)


def _gen_displacement(sensor_id: int, ts: datetime) -> tuple:
    st = _state(sensor_id, {"disp": 0.0})
    st["disp"] += random.gauss(0.003, 0.08)
    st["disp"] = max(-300.0, min(300.0, st["disp"]))
    return round(st["disp"], 3), None, None


def _gen_temperature(sensor_id: int, ts: datetime) -> tuple:
    hour = ts.hour + ts.minute / 60.0
    cycle = math.sin(math.pi * (hour - 4) / 12.0)
    v1 = 29.0 + 6.0 * cycle + random.gauss(0, 0.3)
    return round(v1, 2), None, None


_GENERATORS = {
    "rain":         _gen_rain,
    "tilt":         _gen_tilt,
    "vibration":    _gen_vibration,
    "displacement": _gen_displacement,
    "temperature":  _gen_temperature,
}


# Tra cứu sensor từ DB
def fetch_hanoi_sensors(db) -> list[dict]:
    sql = text("""
        SELECT
            se.sensor_id,
            se.station_id,
            st.area_id,
            se.type_code
        FROM sensors se
        JOIN stations st ON st.station_id = se.station_id
        WHERE st.area_id    = 4
          AND se.status     = 'active'
          AND st.status     = 'active'
        ORDER BY se.station_id, se.type_code, se.sensor_id
    """)

    rows = db.execute(sql).mappings().all()

    if not rows:
        log.error("Không tìm thấy sensor nào cho area_id=4. ")
        sys.exit(1)

    sensors = [dict(r) for r in rows]
    log.info("Tìm thấy %d sensor thuộc khu vực Hà Nội:", len(sensors))
    for s in sensors:
        log.info(
            "  sensor_id=%-4d  station_id=%-4d  type=%s",
            s["sensor_id"], s["station_id"], s["type_code"],
        )
    return sensors


# Sinh payload cho 1 sensor tại 1 thời điểm
def make_payload(sensor: dict, ts: datetime) -> SensorReadingCreate:
    gen_fn = _GENERATORS.get(sensor["type_code"])
    if gen_fn is None:
        raise ValueError(f"Không có generator cho type_code={sensor['type_code']!r}")

    v1, v2, v3 = gen_fn(sensor["sensor_id"], ts)
    quality_flag = 1 if random.random() < 0.01 else 0   # ~1 % suspect

    return SensorReadingCreate(
        timestamp=ts,
        area_id=sensor["area_id"],
        station_id=sensor["station_id"],
        sensor_id=sensor["sensor_id"],
        sensor_type=sensor["type_code"],
        value_1=v1,
        value_2=v2,
        value_3=v3,
        quality_flag=quality_flag,
    )


# Main loop 
def run(interval_seconds: int, dry_run: bool) -> None:
    db = SessionLocal()
    try:
        sensors = fetch_hanoi_sensors(db)
        service = SensorReadingService(db)

        log.info(
            "Bắt đầu sinh dữ liệu realtime — interval=%ds | dry_run=%s | "
            "Nhấn Ctrl+C để dừng.",
            interval_seconds, dry_run,
        )

        while True:
            ts = datetime.now(tz=timezone.utc)
            inserted = 0

            for sensor in sensors:
                payload = make_payload(sensor, ts)

                if dry_run:
                    log.debug(
                        "[DRY-RUN] sensor_id=%d type=%-14s v1=%s v2=%s v3=%s",
                        payload.sensor_id, payload.sensor_type,
                        payload.value_1, payload.value_2, payload.value_3,
                    )
                    inserted += 1
                else:
                    service.create_sensor_reading(payload)
                    inserted += 1

            log.info(
                "%s  %d bản ghi %s",
                ts.isoformat(timespec="seconds"),
                inserted,
                "(dry-run)" if dry_run else "đã INSERT",
            )
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        log.info("Dừng theo yêu cầu.")
    finally:
        db.close()


# CLI
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Sinh dữ liệu realtime vào sensor_readings cho 2 trạm Hà Nội",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--interval-seconds", type=int, default=60,
        help="Khoảng cách giữa 2 lần ghi (giây)",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Chỉ in log, không INSERT vào DB",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(
        interval_seconds=args.interval_seconds,
        dry_run=args.dry_run,
    )