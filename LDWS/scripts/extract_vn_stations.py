import pandas as pd
from pathlib import Path

def main():
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    RAW_DATA_DIR = BASE_DIR / "data" / "raw"
    PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
    
    # Tạo thư mục nếu chưa có
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    input_file = RAW_DATA_DIR / "ghcnd-stations.csv"
    output_file = PROCESSED_DATA_DIR / "vietnam_stations.csv"

    # Kiểm tra xem file gốc đã được đặt đúng chỗ chưa
    if not input_file.exists():
        print(f"Không tìm thấy file gốc tại: {input_file}")
        return

    print(f"Đang bắt đầu lọc dữ liệu từ: {input_file.name}...")

    try:
        # Đọc và xử lý dữ liệu
        # Sử dụng engine='python' để xử lý các dòng có dấu phẩy trong tên trạm
        df = pd.read_csv(
            input_file, 
            header=None, 
            engine='python', 
            on_bad_lines='warn'
        )

        # Đặt tên cột theo chuẩn NOAA
        df.columns = [
            "station_id", "latitude", "longitude", "elevation", 
            "state", "station_name", "gsn_flag", "hcn_flag", "wmo_id"
        ]

        # Lọc các trạm Việt Nam (Mã VM)
        vn_stations = df[df['station_id'].str.startswith('VM', na=False)].copy()

        # Làm sạch tên trạm
        vn_stations['station_name'] = vn_stations['station_name'].str.strip()

        # Xuất kết quả
        vn_stations.to_csv(output_file, index=False, encoding="utf-8-sig")
        
        print(f"DONE!")
        print(f"Tìm thấy: {len(vn_stations)} trạm tại Việt Nam.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()