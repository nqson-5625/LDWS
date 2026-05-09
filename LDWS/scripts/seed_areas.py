import csv
from collections import OrderedDict
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.enums import ActiveInactiveStatus
from app.db.session import SessionLocal
from app.schemas.area import AreaCreate
from app.services.area_service import AreaService

BASE_DIR = Path(__file__).resolve().parent.parent 
CSV_PATH = BASE_DIR / "data" / "processed" / "vietnam_stations.csv"

def normalize_station_name(value: str) -> str:
    return value.strip().upper()


STATION_TO_MERGED_AREA = {
    "NOIBAI INTL": "Hà Nội",
    "HA DONG": "Hà Nội",
    "SON LA": "Sơn La",
    "CAO BANG": "Cao Bằng",
    "LANG SON": "Lạng Sơn",
    "PHU LIEN": "Hải Phòng",
    "THANH HOA": "Thanh Hóa",
    "VINH": "Nghệ An",
    "DONG HOI": "Quảng Trị",
    "DONG HA": "Quảng Trị",
    "QUANG TRI": "Quảng Trị",
    "KHE SANH CWT 5": "Quảng Trị",
    "VANDERGRIF": "Quảng Trị",
    "HUE": "Thành phố Huế",
    "PHONG DENH": "Thành phố Huế",
    "DA NANG": "Thành phố Đà Nẵng",
    "DANANG INTL": "Thành phố Đà Nẵng",
    "MARBLE MTN": "Thành phố Đà Nẵng",
    "CHU LAI": "Thành phố Đà Nẵng",
    "KY HA": "Thành phố Đà Nẵng",
    "AN HOA": "Thành phố Đà Nẵng",
    "PLEIKU": "Gia Lai",
    "AN KHE": "Gia Lai",
    "QUI NHON": "Gia Lai",
    "PHU CAT": "Gia Lai",
    "DRAGON MTN": "Gia Lai",
    "OASIS": "Gia Lai",
    "JACKSON HOLE": "Gia Lai",
    "BAN ME THUOT": "Đắk Lắk",
    "TUY HOA": "Đắk Lắk",
    "NHA TRANG": "Khánh Hòa",
    "CAM RANH BAY": "Khánh Hòa",
    "PHAN RANG": "Khánh Hòa",
    "DA LAT": "Lâm Đồng",
    "PHAN THIET": "Lâm Đồng",
    "BIEN HOA": "Đồng Nai",
    "LONG GIAO": "Đồng Nai",
    "LONG THANH": "Đồng Nai",
    "SAIGON": "Thành phố Hồ Chí Minh",
    "TAN SON HOA": "Thành phố Hồ Chí Minh",
    "CAT LAI": "Thành phố Hồ Chí Minh",
    "CU CHI": "Thành phố Hồ Chí Minh",
    "PHU LOI": "Thành phố Hồ Chí Minh",
    "BEN CAT": "Thành phố Hồ Chí Minh",
    "DI AN": "Thành phố Hồ Chí Minh",
    "PHUOC VINH": "Thành phố Hồ Chí Minh",
    "VUNG TAU": "Thành phố Hồ Chí Minh",
    "TAY NINH": "Tây Ninh",
    "DAU TIENG": "Tây Ninh",
    "TAN AN": "Tây Ninh",
    "BINH THUY": "Thành phố Cần Thơ",
    "SOC TRANG": "Thành phố Cần Thơ",
    "VINH LONG": "Vĩnh Long",
    "DONG TAM": "Đồng Tháp",
    "CA MAU": "Cà Mau",
    "PHU QUOC": "An Giang",
}


AREA_DESCRIPTIONS = {
    "Hà Nội": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Sơn La": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Cao Bằng": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Lạng Sơn": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Hải Phòng": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Thanh Hóa": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Nghệ An": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Quảng Trị": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Thành phố Huế": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Thành phố Đà Nẵng": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Gia Lai": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Đắk Lắk": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Khánh Hòa": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Lâm Đồng": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Đồng Nai": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Thành phố Hồ Chí Minh": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Tây Ninh": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Thành phố Cần Thơ": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Vĩnh Long": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Đồng Tháp": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "Cà Mau": "Area tạo từ NOAA GHCND station list (Việt Nam)",
    "An Giang": "Area tạo từ NOAA GHCND station list (Việt Nam)",
}


def extract_merged_areas_from_csv(csv_path: Path) -> tuple[list[str], list[str]]:
    unique_areas = OrderedDict()
    unmapped_stations = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            station_name = normalize_station_name(row["station_name"])
            merged_area_name = STATION_TO_MERGED_AREA.get(station_name)

            if not merged_area_name:
                unmapped_stations.append(station_name)
                continue

            unique_areas.setdefault(merged_area_name, True)

    return list(unique_areas.keys()), sorted(set(unmapped_stations))


def main():
    db: Session = SessionLocal()
    service = AreaService(db)

    try:
        area_names, unmapped_stations = extract_merged_areas_from_csv(CSV_PATH)

        print("Merged areas extracted from CSV:")
        for name in area_names:
            print(f" - {name}")

        if unmapped_stations:
            print("\n[WARNING] Unmapped station_name values:")
            for name in unmapped_stations:
                print(f" - {name}")

        inserted = 0
        skipped = 0

        for area_name in area_names:
            try:
                service.create_area(
                    AreaCreate(
                        area_name=area_name,
                        description=AREA_DESCRIPTIONS.get(area_name, "Area tạo từ station CSV"),
                        latitude=None,
                        longitude=None,
                        status=ActiveInactiveStatus.ACTIVE,
                    )
                )
                inserted += 1
                print(f"[INSERT] {area_name}")
            except Exception as exc:
                # Nếu bị duplicate thì service sẽ báo lỗi 400
                if "already exists" in str(exc):
                    skipped += 1
                    print(f"[SKIP] Area already exists: {area_name}")
                else:
                    raise

        print(f"\nDone. inserted={inserted}, skipped={skipped}, total_detected={len(area_names)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()