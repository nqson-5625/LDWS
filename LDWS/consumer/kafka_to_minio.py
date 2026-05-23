import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

import boto3
import pandas as pd
from kafka import KafkaConsumer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.core.config import settings

BATCH_SIZE     = 50    # flush khi buffer đủ N bản ghi
FLUSH_INTERVAL = 30    # flush dù chưa đủ batch, sau N giây

TOPICS = [
    "ldws_server.public.areas",
    "ldws_server.public.stations",
    "ldws_server.public.sensors",
    "ldws_server.public.sensor_readings",
    "ldws_server.public.derived_features",
    "ldws_server.public.alert_events",
    "ldws_server.public.alert_status",
]


# Kafka consumer
consumer = KafkaConsumer(
    *TOPICS,
    bootstrap_servers=settings.kafka_bootstrap,
    api_version=(2, 8, 1),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id=settings.kafka_group,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)

s3 = boto3.client(
    "s3",
    endpoint_url=settings.minio_endpoint,
    aws_access_key_id=settings.minio_access_key,
    aws_secret_access_key=settings.minio_secret_key,
)

bucket = settings.minio_bucket

# Tạo bucket nếu chưa tồn tại
existing_buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]
if bucket not in existing_buckets:
    s3.create_bucket(Bucket=bucket)
    print(f"Created bucket: {bucket}")



# Ghi batch ra MinIO dưới dạng Parquet
def write_to_minio(table_name: str, records: list[dict]) -> None:
    if not records:
        return

    df = pd.DataFrame(records)
    date_str = datetime.now().strftime("%Y-%m-%d")
    local_path = f"{table_name}_{date_str}.parquet"

    df.to_parquet(local_path, engine="fastparquet", index=False)

    s3_key = (
        f"{table_name}/date={date_str}/"
        f"{table_name}_{datetime.now().strftime('%H%M%S%f')}.parquet"
    )
    s3.upload_file(local_path, bucket, s3_key)

    Path(local_path).unlink()  # dọn file tạm

    print(f"[upload] {len(records):>5} records → s3://{bucket}/{s3_key}")


# Main consumer loop
buffer     = {topic: [] for topic in TOPICS}
last_flush = {topic: time.time() for topic in TOPICS}

print(f"Connected to Kafka ({settings.kafka_bootstrap}). Listening on {len(TOPICS)} topics...")

try:
    while True:
        # poll() trả về ngay sau timeout_ms dù không có message,
        # để vòng lặp time-based flush bên dưới vẫn chạy đều
        poll_results = consumer.poll(timeout_ms=1000)

        for tp, messages in poll_results.items():
            topic = tp.topic
            for message in messages:
                event = message.value

                if event is None:
                    continue

                payload = event.get("payload", {})
                record  = payload.get("after")  # chỉ lấy trạng thái sau thay đổi

                if record:
                    buffer[topic].append(record)

            # Flush ngay nếu buffer đã đủ BATCH_SIZE
            if len(buffer[topic]) >= BATCH_SIZE:
                table_name = topic.split(".")[-1]
                write_to_minio(table_name, buffer[topic])
                buffer[topic]     = []
                last_flush[topic] = time.time()

        # Đẩy những topic đang chờ quá FLUSH_INTERVAL giây
        now = time.time()
        for topic in TOPICS:
            if buffer[topic] and (now - last_flush[topic]) >= FLUSH_INTERVAL:
                table_name = topic.split(".")[-1]
                print(f"[time-flush] {table_name}: {len(buffer[topic])} records after {FLUSH_INTERVAL}s")
                write_to_minio(table_name, buffer[topic])
                buffer[topic]     = []
                last_flush[topic] = now

except KeyboardInterrupt:
    print("\nStopped by user. Flushing remaining buffers...")
    for topic, records in buffer.items():
        if records:
            write_to_minio(topic.split(".")[-1], records)
    print("Done.")

except Exception as e:
    print(f"\nERROR in consumer loop: {e}", flush=True)
    traceback.print_exc()

finally:
    consumer.close()