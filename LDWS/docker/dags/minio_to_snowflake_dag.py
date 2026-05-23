import os
import boto3
import snowflake.connector
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta


MINIO_ENDPOINT   = os.getenv("INTERNAL_MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
BUCKET           = os.getenv("MINIO_BUCKET")
LOCAL_DIR        = os.getenv("MINIO_LOCAL_DIR", "/tmp/minio_downloads")

SNOWFLAKE_USER      = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD  = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT   = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DB        = os.getenv("SNOWFLAKE_DB")      
SNOWFLAKE_SCHEMA    = os.getenv("SNOWFLAKE_SCHEMA")  


TABLES = [
    "areas",
    "stations",
    "sensors",
    "sensor_readings",
    "derived_features",
    "alert_events",
    "alert_status",
]


# Download Parquet files từ MinIO về local container
def download_from_minio():
    os.makedirs(LOCAL_DIR, exist_ok=True)

    s3 = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )

    file_manifest = {}
    for table in TABLES:
        prefix = f"{table}/"
        paginator = s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=BUCKET, Prefix=prefix)

        file_manifest[table] = []
        for page in pages:
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if "archive/" in key:
                    continue

                local_path = os.path.join(LOCAL_DIR, os.path.basename(key))
                s3.download_file(BUCKET, key, local_path)
                print(f"Downloaded {key} -> {local_path}")
                file_manifest[table].append({"local_path": local_path, "s3_key": key})

    return file_manifest


# Load Parquet vào Snowflake RAW, sau đó archive file trên MinIO
def load_to_snowflake(ti):
    file_manifest = ti.xcom_pull(task_ids="download_minio")
    if not file_manifest:
        print("No files found in MinIO.")
        return

    s3 = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )

    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DB,
        schema=SNOWFLAKE_SCHEMA,
    )
    cur = conn.cursor()

    try:
        for table, file_infos in file_manifest.items():
            if not file_infos:
                print(f"No files for {table}, skipping.")
                continue

            # PUT: upload file từ container lên Snowflake internal stage
            for file_info in file_infos:
                safe_path = file_info["local_path"].replace("\\", "/")
                cur.execute(f"PUT 'file://{safe_path}' @%{table} AUTO_COMPRESS=FALSE")
                print(f"Staged {safe_path} -> @{table}")

            # COPY INTO: load từ stage vào bảng RAW (variant column V)
            cur.execute(f"""
                COPY INTO {table} (V)
                FROM (
                    SELECT $1
                    FROM @%{table}
                )
                FILE_FORMAT = (TYPE = PARQUET)
                PURGE = TRUE
                ON_ERROR = 'CONTINUE'
            """)
            print(f"Loaded data into Snowflake table: {table}")

            # Dọn dẹp: xoá file local + archive file trên MinIO
            for file_info in file_infos:
                if os.path.exists(file_info["local_path"]):
                    os.remove(file_info["local_path"])

                archive_key = f"archive/{file_info['s3_key']}"
                s3.copy_object(
                    Bucket=BUCKET,
                    CopySource=f"{BUCKET}/{file_info['s3_key']}",
                    Key=archive_key,
                )
                s3.delete_object(Bucket=BUCKET, Key=file_info["s3_key"])
                print(f"Archived {file_info['s3_key']} -> {archive_key}")

    finally:
        cur.close()
        conn.close()


# DAG definition
default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="minio_to_snowflake_landslide",
    default_args=default_args,
    description="Load MinIO parquet into Snowflake RAW tables (landslide)",
    schedule_interval="*/1 * * * *",  
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,  # tránh 2 run đồng thời download/archive cùng 1 file
) as dag:

    task_download = PythonOperator(
        task_id="download_minio",
        python_callable=download_from_minio,
    )

    task_load = PythonOperator(
        task_id="load_snowflake",
        python_callable=load_to_snowflake,
    )

    task_download >> task_load