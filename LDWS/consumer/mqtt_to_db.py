import json
import time
import logging
import threading
import queue
import sys
from pathlib import Path
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
from sqlalchemy import text

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.repositories import SensorRepository, SensorReadingRepository

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s",
)
log = logging.getLogger(__name__)

# CẤU HÌNH HỆ THỐNG 
MQTT_BROKER = settings.mqtt_broker
MQTT_PORT = settings.mqtt_port
MQTT_TOPIC = "ldws/data/station/+/sensor/+"
BATCH_SIZE = 50           # Số lượng bản ghi tối đa trong 1 lô (batch)
FLUSH_INTERVAL = 2.0      # Thời gian tối đa (giây) chờ để ghi lô dữ liệu vào DB
MAX_RETRIES = 3           # Số lần thử lại tối đa nếu Database bị rớt
RETRY_DELAY = 5.0         # Thời gian chờ giữa các lần thử lại (giây)

# Hàng đợi lưu trữ message tạm thời trên RAM
message_queue = queue.Queue(maxsize=10000)

# Bộ đệm Cache ánh xạ sensor_code -> sensor_id
sensor_cache = {}


def load_sensor_cache():
    global sensor_cache
    log.info("Đang tải dữ liệu ánh xạ Sensor từ Database...")
    db = SessionLocal()
    try:
        # Truy vấn toàn bộ sensor đang active
        sensor_repo = SensorRepository(db)
        active_sensors = sensor_repo.list_active()

        for sensor in active_sensors:
            sensor_cache[sensor.sensor_code] = sensor.sensor_id
        log.info(f"Đã tải thành công {len(sensor_cache)} sensors vào Cache.")
    except Exception as e:
        log.error(f"Lỗi khi tải Sensor Cache: {e}")
        raise e
    finally:
        db.close()


def db_writer_worker():
    buffer = []
    last_flush_time = time.time()

    while True:
        try:
            # Lấy message từ Queue với timeout để không bị block hoàn toàn
            msg = message_queue.get(timeout=0.5)
            buffer.append(msg)
        except queue.Empty:
            pass # Queue rỗng, tiếp tục kiểm tra điều kiện flush

        # Điều kiện để Flush (ghi vào DB): Đủ số lượng (BATCH_SIZE) hoặc Đủ thời gian (FLUSH_INTERVAL)
        current_time = time.time()
        if len(buffer) >= BATCH_SIZE or (len(buffer) > 0 and current_time - last_flush_time >= FLUSH_INTERVAL):
            success = flush_to_db(buffer)
            
            if success:
                buffer.clear() # Xóa buffer nếu ghi thành công
                last_flush_time = time.time()
            else:
                # Nếu ghi thất bại (đã hết số lần retry), giữ lại buffer và thử lại ở vòng lặp sau
                log.warning(f"Giữ lại {len(buffer)} bản ghi trong buffer để thử lại sau.")
                time.sleep(RETRY_DELAY)


def flush_to_db(batch_data: list) -> bool:
    db = SessionLocal()
    retries = 0

    # Chuyển đổi dữ liệu từ format MQTT payload sang format tương thích với DB
    insert_payloads = []
    for item in batch_data:
        sensor_code = item.get("sensor_code")
        sensor_id = sensor_cache.get(sensor_code)
        
        if not sensor_id:
            log.warning(f"Bỏ qua dữ liệu: Không tìm thấy sensor_id cho mã {sensor_code}")
            continue
            
        insert_payloads.append({
            "timestamp": item["timestamp"],
            "area_id": item["area_id"],
            "station_id": item["station_id"],
            "sensor_id": sensor_id,
            "sensor_type": item["sensor_type"],
            "value_1": item["value_1"],
            "value_2": item["value_2"],
            "value_3": item["value_3"],
            "quality_flag": item["quality_flag"]
        })

    if not insert_payloads:
        db.close()
        return True
    
    reading_repo = SensorReadingRepository(db)

    while retries < MAX_RETRIES:
        try:
            # Thực thi Bulk Insert trong 1 Transaction duy nhất
            inserted_count = reading_repo.bulk_insert(insert_payloads)
            log.info(f"Đã lưu thành công lô {len(insert_payloads)} bản ghi vào Database.")
            return True
            
        except Exception as e:
            db.rollback()
            retries += 1
            log.error(f"Lỗi ghi Database (lần thử {retries}/{MAX_RETRIES}): {e}")
            if retries < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
    
    db.close()
    return False # Trả về False để Worker biết là phải giữ lại buffer


def on_mqtt_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        
        # Đẩy dữ liệu ngay lập tức vào Queue và thoát hàm (Non-blocking I/O)
        message_queue.put(payload, block=False)
        
    except queue.Full:
        log.error("Hàng đợi đã đầy! Đang đánh rơi tin nhắn để tránh tràn bộ nhớ.")
    except Exception as e:
        log.error(f"Lỗi phân tích cú pháp MQTT payload: {e}")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        log.info("Đã kết nối tới MQTT Broker. Bắt đầu lắng nghe dữ liệu...")
        client.subscribe(MQTT_TOPIC, qos=1)
    else:
        log.error(f"Không thể kết nối tới Broker. Mã lỗi: {rc}")


if __name__ == "__main__":
    # Khởi tạo Cache ánh xạ ID
    load_sensor_cache()

    # Khởi động tiểu trình (Thread) ghi dữ liệu vào DB (Giải quyết #3: Blocking I/O)
    writer_thread = threading.Thread(target=db_writer_worker, name="DBWriter")
    writer_thread.daemon = True # Thread sẽ tự tắt khi tiến trình chính kết thúc
    writer_thread.start()

    # Thiết lập MQTT Consumer
    mqtt_client = mqtt.Client(client_id="LDWS_Database_Writer")
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_mqtt_message

    # Khởi tạo kết nối vòng lặp
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        # Sử dụng loop_forever ở luồng chính (Main thread) để giữ kết nối MQTT
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        log.info("Đang ngắt kết nối an toàn...")
        mqtt_client.disconnect()