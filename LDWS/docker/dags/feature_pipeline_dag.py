import os
import psycopg2
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta


PG_HOST     = os.getenv("INTERNAL_POSTGRES_HOST")
PG_PORT     = os.getenv("INTERNAL_POSTGRES_PORT", "5432")
PG_USER     = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_DB       = os.getenv("POSTGRES_DB")

# LATE_DATA_BUFFER: Bộ đệm thời gian chờ dữ liệu trễ
# Quét và cập nhật lại toàn bộ 5 phút gần nhất để lấy mọi dữ liệu gửi muộn
LATE_DATA_BUFFER = timedelta(minutes=5)


def get_pg_conn():
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DB,
    )


def compute_derived_features(**context):
    execution_ts = context["data_interval_end"] # Thời điểm hiện tại của DAG
    window_end   = execution_ts # Điểm kết thúc của cửa sổ trượt (ngay tại lúc chạy DAG)
    window_start = window_end - timedelta(days=3) # Điểm bắt đầu quét dữ liệu thô (3 ngày trước)
    bucket_start = window_end - LATE_DATA_BUFFER # Điểm bắt đầu quét dữ liệu trễ (5 phút trước)

    # Logic Transform
    sql_upsert = """
        WITH

        -- Aggregate DỮ LIỆU THÔ thành các bucket 1 phút (pivot + aggregate)
        raw_data AS MATERIALIZED ( -- MATERIALIZED để tránh tính toán lại nhiều lần trong cùng 1 transaction
            SELECT
                time_bucket('1 minute', "timestamp")  AS bucket, -- Bucket 1 phút
                area_id,
                station_id,

                -- COALESCE: Nếu không có sensor nào trong bucket đó, trả về 0 thay vì NULL

                -- Rain
                COALESCE(SUM(value_1)  FILTER (WHERE sensor_type = 'rain'), 0) AS rain_sum,
                COALESCE(AVG(value_1)  FILTER (WHERE sensor_type = 'rain'), 0) AS rain_avg,

                -- Tilt
                COALESCE(MAX(ABS(value_1)) FILTER (WHERE sensor_type = 'tilt'), 0) AS tilt_max_abs,
                COALESCE(MAX(value_1)      FILTER (WHERE sensor_type = 'tilt'), 0) AS tilt_val,

                -- Displacement
                COALESCE(MAX(value_1) FILTER (WHERE sensor_type = 'displacement'), 0) AS disp_val,

                -- Vibration
                COALESCE(AVG(value_1) FILTER (WHERE sensor_type = 'vibration'), 0) AS vib_avg,
                COALESCE(MAX(value_1) FILTER (WHERE sensor_type = 'vibration'), 0) AS vib_peak,

                -- Temperature
                COALESCE(AVG(value_1) FILTER (WHERE sensor_type = 'temperature'), 0) AS temp_avg

            FROM sensor_readings
            
            -- Chỉ quét 1 lần duy nhất toàn bộ dữ liệu 3 ngày qua của tất cả các trạm
            WHERE "timestamp" >= %(window_start)s
              AND "timestamp" <  %(window_end)s
            GROUP BY
                time_bucket('1 minute', "timestamp"),
                area_id,
                station_id
        ),

        -- TÍNH CỘNG DỒN CHO MƯA (ROLLING_RAIN)
        rolling_rain AS (
            SELECT
                bucket,
                area_id,
                station_id,

                -- SUM(...) OVER w_1h: Cộng dồn tất cả rain_sum của các dòng thuộc 
                -- cùng 1 trạm (PARTITION) nằm trong khoảng thời gian 1 giờ trước đó (RANGE)
                SUM(rain_sum) OVER w_1h  AS rain_1h,
                SUM(rain_sum) OVER w_3h  AS rain_3h,
                SUM(rain_sum) OVER w_24h AS rain_24h,
                SUM(rain_sum) OVER w_3d  AS rain_3d,
                AVG(rain_avg) OVER w_1h  AS rain_intensity
            FROM raw_data

            WINDOW
                -- Khai báo các khung cửa sổ trượt (Sliding Windows)
                w_1h  AS (PARTITION BY station_id ORDER BY bucket
                          RANGE BETWEEN INTERVAL '1 hour'  PRECEDING AND CURRENT ROW),
                w_3h  AS (PARTITION BY station_id ORDER BY bucket
                          RANGE BETWEEN INTERVAL '3 hours' PRECEDING AND CURRENT ROW),
                w_24h AS (PARTITION BY station_id ORDER BY bucket
                          RANGE BETWEEN INTERVAL '24 hours' PRECEDING AND CURRENT ROW),
                w_3d  AS (PARTITION BY station_id ORDER BY bucket
                          RANGE BETWEEN INTERVAL '3 days'  PRECEDING AND CURRENT ROW)
        ),

        -- TÍNH ĐỘ LỆCH BẰNG SNAPSHOT (POINT_IN_TIME)
        point_in_time AS (
            SELECT
                r.bucket,
                r.station_id,

                -- Tilt
                r.tilt_max_abs AS tilt_value,
                -- Độ lệch 1h = Giá trị phút này trừ đi (-) Giá trị của đúng 1 tiếng trước (r1h)
                r.tilt_val - COALESCE(r1h.tilt_val,  r.tilt_val) AS tilt_change_1h,
                r.tilt_val - COALESCE(r24h.tilt_val, r.tilt_val) AS tilt_change_24h,

                -- Displacement
                r.disp_val                                        AS disp_value,
                r.disp_val - COALESCE(r1h.disp_val,  r.disp_val) AS disp_change_1h,
                r.disp_val - COALESCE(r24h.disp_val, r.disp_val) AS disp_change_24h,

                -- Vibration & Temperature (không cần point-in-time)
                r.vib_avg   AS vibration_value,
                r.vib_peak  AS vibration_peak,
                r.temp_avg  AS temperature_value

            FROM raw_data r

            -- Snapshot tại bucket - 1h
            -- LATERAL JOIN: Vòng lặp For của SQL. 
            -- Với mỗi dòng (r) ở bảng raw_data, nó sẽ chạy câu SELECT con này 1 lần
            -- để đi tìm đúng cái dòng nằm cách nó 1 tiếng đồng hồ (snapshot).
            LEFT JOIN LATERAL (
                SELECT tilt_val, disp_val
                FROM raw_data
                WHERE station_id = r.station_id
                  -- Tìm bucket <= bucket hiện tại - 1h
                  AND bucket <= r.bucket - INTERVAL '1 hour'
                -- Sắp xếp giảm dần và lấy dòng trên cùng (LIMIT 1) -> Dòng gần mốc 1h nhất
                ORDER BY bucket DESC
                LIMIT 1
            ) AS r1h ON true

            -- Snapshot tại bucket - 24h
            LEFT JOIN LATERAL (
                SELECT tilt_val, disp_val
                FROM raw_data
                WHERE station_id = r.station_id
                  AND bucket <= r.bucket - INTERVAL '24 hours'
                ORDER BY bucket DESC
                LIMIT 1
            ) AS r24h ON true
        )

        -- GHI DỮ LIỆU LÊN DATABASE (UPSERT)
        INSERT INTO derived_features (
            "timestamp", area_id, station_id,
            rain_1h, rain_3h, rain_24h, rain_3d, rain_intensity,
            tilt_value, tilt_rate, tilt_change_1h, tilt_change_24h,
            disp_value, disp_rate, disp_change_1h, disp_change_24h,
            vibration_value, vibration_peak, vibration_flag,
            temperature_value, temperature_flag,
            anomaly_score, anomaly_flag, risk_score, alert_level_candidate
        )
        SELECT
            rr.bucket,
            rr.area_id,
            rr.station_id,

            -- Lược qua các dòng COALESCE để làm sạch NULL

            -- Rain
            COALESCE(rr.rain_1h,        0),
            COALESCE(rr.rain_3h,        0),
            COALESCE(rr.rain_24h,       0),
            COALESCE(rr.rain_3d,        0),
            COALESCE(rr.rain_intensity, 0),

            -- Tilt (tilt_rate = change_1h, đơn vị độ/giờ)
            COALESCE(pt.tilt_value,      0),
            COALESCE(pt.tilt_change_1h,  0),    -- tilt_rate
            COALESCE(pt.tilt_change_1h,  0),
            COALESCE(pt.tilt_change_24h, 0),

            -- Displacement (disp_rate = change_1h, đơn vị mm/giờ)
            COALESCE(pt.disp_value,      0),
            COALESCE(pt.disp_change_1h,  0),    -- disp_rate
            COALESCE(pt.disp_change_1h,  0),
            COALESCE(pt.disp_change_24h, 0),

            -- Vibration
            COALESCE(pt.vibration_value, 0),
            COALESCE(pt.vibration_peak,  0),
            COALESCE(pt.vibration_peak > 0.1, false),

            -- Temperature
            COALESCE(pt.temperature_value,      0),
            COALESCE(pt.temperature_value > 38, false),

            -- Chưa tính
            NULL::FLOAT,    -- anomaly_score
            false,          -- anomaly_flag
            NULL::FLOAT,    -- risk_score
            NULL::SMALLINT   -- alert_level_candidate

        FROM rolling_rain rr
        -- Ráp cột mưa và cột snapshot lệch giờ lại với nhau
        JOIN point_in_time pt
            ON  pt.bucket     = rr.bucket
            AND pt.station_id = rr.station_id
        WHERE rr.bucket >= %(bucket_start)s -- CHỈ lấy kết quả của 5 PHÚT CUỐI CÙNG để ghi vào DB


        -- CƠ CHẾ UPSERT (Idempotency)
        ON CONFLICT (station_id, "timestamp")
        DO UPDATE SET
            rain_1h           = EXCLUDED.rain_1h,
            rain_3h           = EXCLUDED.rain_3h,
            rain_24h          = EXCLUDED.rain_24h,
            rain_3d           = EXCLUDED.rain_3d,
            rain_intensity    = EXCLUDED.rain_intensity,
            tilt_value        = EXCLUDED.tilt_value,
            tilt_rate         = EXCLUDED.tilt_rate,
            tilt_change_1h    = EXCLUDED.tilt_change_1h,
            tilt_change_24h   = EXCLUDED.tilt_change_24h,
            disp_value        = EXCLUDED.disp_value,
            disp_rate         = EXCLUDED.disp_rate,
            disp_change_1h    = EXCLUDED.disp_change_1h,
            disp_change_24h   = EXCLUDED.disp_change_24h,
            vibration_value   = EXCLUDED.vibration_value,
            vibration_peak    = EXCLUDED.vibration_peak,
            vibration_flag    = EXCLUDED.vibration_flag,
            temperature_value = EXCLUDED.temperature_value,
            temperature_flag  = EXCLUDED.temperature_flag
    """

    conn = get_pg_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql_upsert, {
                "window_start": window_start,
                "window_end":   window_end,
                "bucket_start": bucket_start,
            })
            affected = cur.rowcount
        conn.commit()
        print(
            f"[feature_pipeline] {affected} rows upserted | "
            f"buckets: {bucket_start} → {window_end} | "
            f"scan window: {window_start} → {window_end}"
        )
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()



# DAG definition
default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="feature_pipeline_landslide",
    default_args=default_args,
    description="Tính derived_features — pivot + window function + LATERAL join",
    schedule_interval="*/5 * * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
) as dag:

    task_compute = PythonOperator(
        task_id="compute_derived_features",
        python_callable=compute_derived_features,
    )