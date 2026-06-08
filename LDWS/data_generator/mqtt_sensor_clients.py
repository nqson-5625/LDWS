import time
import random
import json
import math
import threading
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.core.config import settings

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s",
)
log = logging.getLogger(__name__)


# DANH SÁCH 18 SENSORS 
SENSORS_CONFIG = [
    # NOIBAI INTL station
    {"area_id": 4, "station_id": 1, "type_code": "rain", "sensor_code": "HN-NBI-RAIN-01"},
    {"area_id": 4, "station_id": 1, "type_code": "tilt", "sensor_code": "HN-NBI-TILT-01"},
    {"area_id": 4, "station_id": 1, "type_code": "tilt", "sensor_code": "HN-NBI-TILT-02"},
    {"area_id": 4, "station_id": 1, "type_code": "vibration", "sensor_code": "HN-NBI-VIB-01"},
    {"area_id": 4, "station_id": 1, "type_code": "vibration", "sensor_code": "HN-NBI-VIB-02"},
    {"area_id": 4, "station_id": 1, "type_code": "displacement", "sensor_code": "HN-NBI-DISP-01"},
    {"area_id": 4, "station_id": 1, "type_code": "displacement", "sensor_code": "HN-NBI-DISP-02"},
    {"area_id": 4, "station_id": 1, "type_code": "displacement", "sensor_code": "HN-NBI-DISP-03"},
    {"area_id": 4, "station_id": 1, "type_code": "temperature", "sensor_code": "HN-NBI-TEMP-01"},
    
    # HA DONG station
    {"area_id": 4, "station_id": 2, "type_code": "rain", "sensor_code": "HN-HDG-RAIN-01"},
    {"area_id": 4, "station_id": 2, "type_code": "tilt", "sensor_code": "HN-HDG-TILT-01"},
    {"area_id": 4, "station_id": 2, "type_code": "tilt", "sensor_code": "HN-HDG-TILT-02"},
    {"area_id": 4, "station_id": 2, "type_code": "vibration", "sensor_code": "HN-HDG-VIB-01"},
    {"area_id": 4, "station_id": 2, "type_code": "vibration", "sensor_code": "HN-HDG-VIB-02"},
    {"area_id": 4, "station_id": 2, "type_code": "displacement", "sensor_code": "HN-HDG-DISP-01"},
    {"area_id": 4, "station_id": 2, "type_code": "displacement", "sensor_code": "HN-HDG-DISP-02"},
    {"area_id": 4, "station_id": 2, "type_code": "displacement", "sensor_code": "HN-HDG-DISP-03"},
    {"area_id": 4, "station_id": 2, "type_code": "temperature", "sensor_code": "HN-HDG-TEMP-01"},
]


# LOGIC SINH DỮ LIỆU 
class SensorDataGenerator:
    def __init__(self, sensor_code):
        self.sensor_code = sensor_code
        self.state = {}

    def _get_state(self, defaults):
        if not self.state:
            self.state = defaults
        return self.state

    def gen_rain(self, ts):
        st = self._get_state({"active": False, "intensity": 0.0, "remaining": 0})
        if st["active"]:    
            st["remaining"] -= 1
            if st["remaining"] <= 0:
                st["active"] = False
                st["intensity"] = 0.0
            v1 = max(0.0, round(st["intensity"] + random.gauss(0, 0.08), 3))
        else:
            if random.random() < 0.15:
                st["active"] = True
                st["intensity"] = random.uniform(0.05, 2.5)
                st["remaining"] = random.randint(5, 60)
                v1 = round(st["intensity"], 3)
            else:
                v1 = 0.0
        return v1, None, None

    def gen_tilt(self, ts):
        st = self._get_state({"x": random.uniform(-2.0, 2.0), "y": random.uniform(-1.5, 1.5)})
        st["x"] = max(-20.0, min(20.0, st["x"] + random.gauss(0.002, 0.05)))
        st["y"] = max(-20.0, min(20.0, st["y"] + random.gauss(0.001, 0.04)))
        return round(st["x"], 4), round(st["y"], 4), None

    def gen_vibration(self, ts):
        is_reference = "02" in self.sensor_code
        base = 0.005 if is_reference else 0.012
        event_mag = random.uniform(0.05, 0.20) if not is_reference and random.random() < 0.02 else 0.0
        return (
            round(abs(random.gauss(base + event_mag, 0.003)), 5),
            round(abs(random.gauss(base + event_mag * 0.8, 0.003)), 5),
            round(abs(random.gauss(base + event_mag * 0.5, 0.003)), 5)
        )

    def gen_displacement(self, ts):
        st = self._get_state({"disp": 0.0})
        st["disp"] = max(-300.0, min(300.0, st["disp"] + random.gauss(0.003, 0.08)))
        return round(st["disp"], 3), None, None

    def gen_temperature(self, ts):
        hour = ts.hour + ts.minute / 60.0
        cycle = math.sin(math.pi * (hour - 4) / 12.0)
        v1 = 29.0 + 6.0 * cycle + random.gauss(0, 0.3)
        return round(v1, 2), None, None

    def generate(self, type_code, ts):
        generators = {
            "rain": self.gen_rain, "tilt": self.gen_tilt, 
            "vibration": self.gen_vibration, "displacement": self.gen_displacement, 
            "temperature": self.gen_temperature
        }
        return generators[type_code](ts)


# ĐỊNH NGHĨA MQTT CLIENT CHO TỪNG SENSOR
class SensorMQTTClient(threading.Thread):
    def __init__(self, config, broker_url=settings.mqtt_broker, broker_port=settings.mqtt_port, interval=2):
        super().__init__(name=config["sensor_code"])
        self.config = config
        self.broker_url = broker_url
        self.broker_port = broker_port
        self.interval = interval
        self.generator = SensorDataGenerator(config["sensor_code"])
        
        # Tạo Client ID duy nhất
        self.client = mqtt.Client(client_id=f"client_{config['sensor_code']}")
        self.client.on_connect = self.on_connect
        
        # Định nghĩa MQTT Topic
        self.topic = f"ldws/data/station/{config['station_id']}/sensor/{config['sensor_code']}"

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            log.info(f"Đã kết nối MQTT Broker thành công.")
        else:
            log.error(f"Kết nối thất bại, mã lỗi: {rc}")

    def run(self):
        self.client.connect(self.broker_url, self.broker_port, 60)
        self.client.loop_start()

        while True:
            ts = datetime.now(tz=timezone.utc)
            v1, v2, v3 = self.generator.generate(self.config["type_code"], ts)
            
            # Khởi tạo payload dạng JSON
            payload = {
                "timestamp": ts.isoformat(),
                "area_id": self.config["area_id"],
                "station_id": self.config["station_id"],
                "sensor_code": self.config["sensor_code"],
                "sensor_type": self.config["type_code"],
                "value_1": v1,
                "value_2": v2,
                "value_3": v3,
                "quality_flag": 1 if random.random() < 0.01 else 0
            }
            
            # Publish dữ liệu lên Broker
            self.client.publish(self.topic, json.dumps(payload), qos=1)
            log.debug(f"Published to {self.topic}: {payload}")
            
            time.sleep(self.interval)


# CHẠY ĐỒNG THỜI 18 CLIENTS
if __name__ == "__main__":
    MQTT_BROKER = settings.mqtt_broker 
    MQTT_PORT = settings.mqtt_port
    INTERVAL = 2 

    log.info("Khởi động 18 MQTT Sensor Clients...")
    threads = []
    
    try:
        for sensor_cfg in SENSORS_CONFIG:
            client_thread = SensorMQTTClient(
                config=sensor_cfg, 
                broker_url=MQTT_BROKER, 
                broker_port=MQTT_PORT, 
                interval=INTERVAL
            )
            client_thread.daemon = True # Thread tự đóng khi app chính đóng
            client_thread.start()
            threads.append(client_thread)
            time.sleep(0.1) # Tránh việc 18 kết nối chớp nhoáng gây quá tải Broker
            
        while True:
            time.sleep(1) # Giữ cho main thread hoạt động
            
    except KeyboardInterrupt:
        log.info("Đã nhận lệnh dừng. Đang ngắt kết nối các sensors...")