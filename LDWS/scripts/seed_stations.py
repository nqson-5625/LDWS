import csv
from pathlib import Path

from fastapi import HTTPException

from app.core.enums import ActiveInactiveStatus
from app.db.session import SessionLocal
from app.schemas.station import StationCreate
from app.services.station_service import StationService


BASE_DIR = Path(__file__).resolve().parent.parent 
CSV_PATH = BASE_DIR / "data" / "processed" / "vietnam_stations.csv"


def normalize_station_name(value: str) -> str:
    return value.strip().upper()


def is_vietnam_station(station_id: str) -> bool:
    return station_id.strip().upper().startswith("VM")


AREA_NAME_TO_ID = {
    "Thành phố Hồ Chí Minh": 1,
    "Sơn La": 2,
    "Cao Bằng": 3,
    "Hà Nội": 4,
    "Hải Phòng": 5,
    "Lạng Sơn": 6,
    "Thanh Hóa": 7,
    "Nghệ An": 8,
    "Quảng Trị": 9,
    "Thành phố Đà Nẵng": 10,
    "Lâm Đồng": 11,
    "Cà Mau": 12,
    "An Giang": 13,
    "Thành phố Cần Thơ": 14,
    "Gia Lai": 15,
    "Vĩnh Long": 16,
    "Thành phố Huế": 17,
    "Đồng Nai": 18,
    "Khánh Hòa": 19,
    "Đắk Lắk": 20,
    "Tây Ninh": 21,
    "Đồng Tháp": 22,
}


# Mapping station_name -> area_id theo ảnh area_id hiện tại
STATION_TO_AREA_ID = {
    "NOIBAI INTL": 4,
    "HA DONG": 4,

    "SON LA": 2,

    "CAO BANG": 3,

    "LANG SON": 6,

    "PHU LIEN": 5,

    "THANH HOA": 7,

    "VINH": 8,

    "DONG HOI": 9,
    "DONG HA": 9,
    "QUANG TRI": 9,
    "KHE SANH CWT 5": 9,
    "VANDERGRIF": 9,

    "HUE": 17,
    "PHONG DENH": 17,

    "DA NANG": 10,
    "DANANG INTL": 10,
    "MARBLE MTN": 10,
    "CHU LAI": 10,
    "KY HA": 10,
    "AN HOA": 10,

    "PLEIKU": 15,
    "AN KHE": 15,
    "QUI NHON": 15,
    "PHU CAT": 15,
    "DRAGON MTN": 15,
    "OASIS": 15,
    "JACKSON HOLE": 15,

    "BAN ME THUOT": 20,
    "TUY HOA": 20,

    "NHA TRANG": 19,
    "CAM RANH BAY": 19,
    "PHAN RANG": 19,

    "DA LAT": 11,
    "PHAN THIET": 11,

    "BIEN HOA": 18,
    "LONG GIAO": 18,
    "LONG THANH": 18,

    "SAIGON": 1,
    "TAN SON HOA": 1,
    "CAT LAI": 1,
    "CU CHI": 1,
    "PHU LOI": 1,
    "BEN CAT": 1,
    "DI AN": 1,
    "PHUOC VINH": 1,
    "VUNG TAU": 1,

    "TAY NINH": 21,
    "DAU TIENG": 21,
    "TAN AN": 21,

    "BINH THUY": 14,
    "SOC TRANG": 14,

    "VINH LONG": 16,

    "DONG TAM": 22,

    "CA MAU": 12,

    "PHU QUOC": 13,
}


def build_location_description(row: dict, area_id: int) -> str:
    elevation = row.get("elevation") or ""
    state = row.get("state") or ""
    parts = [
        f"Imported from NOAA GHCND",
        f"station_id={row.get('station_id', '').strip()}",
        f"area_id={area_id}",
    ]
    if state.strip():
        parts.append(f"state={state.strip()}")
    if elevation.strip():
        parts.append(f"elevation={elevation.strip()} m")
    return " | ".join(parts)


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    return float(value)


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

    db = SessionLocal()
    service = StationService(db)

    inserted = 0
    skipped = 0
    skipped_non_vn = 0
    unmapped = []

    try:
        with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                station_id = row["station_id"].strip()
                station_name = normalize_station_name(row["station_name"])

                # Chỉ lấy trạm Việt Nam
                if not is_vietnam_station(station_id):
                    skipped_non_vn += 1
                    continue

                area_id = STATION_TO_AREA_ID.get(station_name)
                if area_id is None:
                    unmapped.append(
                        {
                            "station_id": station_id,
                            "station_name": station_name,
                            "latitude": row.get("latitude"),
                            "longitude": row.get("longitude"),
                        }
                    )
                    continue

                try:
                    payload = StationCreate(
                        area_id=area_id,
                        station_name=station_name,
                        location_description=build_location_description(row, area_id),
                        latitude=parse_float(row.get("latitude")),
                        longitude=parse_float(row.get("longitude")),
                        elevation=parse_float(row.get("elevation")),
                        status=ActiveInactiveStatus.ACTIVE,
                    )
                    service.create_station(payload)
                    inserted += 1
                    print(f"[INSERT] {station_name} -> area_id={area_id}")

                except HTTPException as exc:
                    if exc.status_code == 400 and "already exists" in str(exc.detail):
                        skipped += 1
                        print(f"[SKIP] Station already exists in area: {station_name} -> area_id={area_id}")
                    else:
                        raise

        print("\n" + "=" * 80)
        print("DONE")
        print("=" * 80)
        print(f"Inserted stations: {inserted}")
        print(f"Skipped existing stations: {skipped}")
        print(f"Skipped non-Vietnam stations: {skipped_non_vn}")
        print(f"Unmapped Vietnam stations: {len(unmapped)}")

        if unmapped:
            print("\nUNMAPPED VIETNAM STATIONS:")
            for item in unmapped:
                print(
                    f"- {item['station_name']} "
                    f"[{item['station_id']}] "
                    f"(lat={item['latitude']}, lon={item['longitude']})"
                )

    finally:
        db.close()


if __name__ == "__main__":
    main()