DROP VIEW IF EXISTS vw_derived_features CASCADE;
DROP MATERIALIZED VIEW IF EXISTS sensor_readings_1m CASCADE;


-- Tạo Caggs gom raw data theo từng phút
CREATE MATERIALIZED VIEW sensor_readings_1m
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', "timestamp") AS bucket,
    area_id,
    station_id,
    
    COALESCE(SUM(value_1)  FILTER (WHERE sensor_type = 'rain'), 0) AS rain_sum,
    COALESCE(AVG(value_1)  FILTER (WHERE sensor_type = 'rain'), 0) AS rain_avg,
    COALESCE(MAX(ABS(value_1)) FILTER (WHERE sensor_type = 'tilt'), 0) AS tilt_max_abs,
    COALESCE(MAX(value_1)      FILTER (WHERE sensor_type = 'tilt'), 0) AS tilt_val,
    COALESCE(MAX(value_1)  FILTER (WHERE sensor_type = 'displacement'), 0) AS disp_val,
    COALESCE(AVG(value_1)  FILTER (WHERE sensor_type = 'vibration'), 0) AS vib_avg,
    COALESCE(MAX(value_1)  FILTER (WHERE sensor_type = 'vibration'), 0) AS vib_peak,
    COALESCE(AVG(value_1)  FILTER (WHERE sensor_type = 'temperature'), 0) AS temp_avg
FROM sensor_readings
GROUP BY bucket, area_id, station_id;

-- Đăng ký chính sách tự động làm mới Caggs mỗi phút
SELECT add_continuous_aggregate_policy(
    'sensor_readings_1m',
    start_offset        => INTERVAL '3 days',   -- Chỉ làm mới dữ liệu trong 3 ngày gần nhất
    end_offset          => INTERVAL '1 minute', -- Lùi lại 1 phút để đảm bảo dữ liệu đã ổn định
    schedule_interval   => INTERVAL '1 minute'  -- Làm mới mỗi phút
);

-- Tạo view tính sliding window features từ Caggs
CREATE OR REPLACE VIEW vw_derived_features AS
SELECT
    bucket AS "timestamp",
    area_id,
    station_id,

    -- Các đặc trưng lượng mưa tích lũy
    SUM(rain_sum) OVER w_1h  AS rain_1h,
    SUM(rain_sum) OVER w_3h  AS rain_3h,
    SUM(rain_sum) OVER w_24h AS rain_24h,
    SUM(rain_sum) OVER w_3d  AS rain_3d,
    AVG(rain_avg) OVER w_1h  AS rain_intensity,
    
    -- Các đặc trưng góc nghiêng
    tilt_max_abs AS tilt_value,
    COALESCE(tilt_val - LAG(tilt_val, 60) OVER (PARTITION BY station_id ORDER BY bucket), 0) AS tilt_rate,
    COALESCE(tilt_val - LAG(tilt_val, 1440) OVER (PARTITION BY station_id ORDER BY bucket), 0) AS tilt_change_24h,
    
    -- Các đặc trưng dịch chuyển khối đất
    disp_val AS disp_value,
    COALESCE(disp_val - LAG(disp_val, 60) OVER (PARTITION BY station_id ORDER BY bucket), 0) AS disp_rate,
    COALESCE(disp_val - LAG(disp_val, 1440) OVER (PARTITION BY station_id ORDER BY bucket), 0) AS disp_change_24h,
    
    -- Rung động và nhiệt độ
    vib_avg AS vibration_value,
    vib_peak AS vibration_peak,
    temp_avg AS temperature_value,
    (vib_peak > 0.1) AS vibration_flag,
    (temp_avg > 38) AS temperature_flag

FROM sensor_readings_1m
WINDOW 
    w_1h  AS (PARTITION BY station_id ORDER BY bucket RANGE BETWEEN INTERVAL '1 hour' PRECEDING AND CURRENT ROW),
    w_3h  AS (PARTITION BY station_id ORDER BY bucket RANGE BETWEEN INTERVAL '3 hours' PRECEDING AND CURRENT ROW),
    w_24h AS (PARTITION BY station_id ORDER BY bucket RANGE BETWEEN INTERVAL '24 hours' PRECEDING AND CURRENT ROW),
    w_3d  AS (PARTITION BY station_id ORDER BY bucket RANGE BETWEEN INTERVAL '3 days' PRECEDING AND CURRENT ROW);

-- tôi đã viết thêm file postgres/continuous_aggregates.sql và cập nhật file app/services/alert/alert_pipeline.py với mục đích thay thế hoàn toàn docker/dags/feature_pipeline_dag.py, bạn hãy kiểm tra xem tôi đã thực hiện chính xác chưa và đã có thể xóa hoàn toàn file docker/dags/feature_pipeline_dag.py hay chưa, nếu được rồi thì bạn hãy đăng ký dịch vụ chạy realtime hoàn chỉnh cho app.services.alert.alert_pipeline vào Docker Compose, hướng dẫn tôi cách để migration file postgres/continuous_aggregates.sql, nếu có lỗi thì hãy chỉ ra và sửa lỗi giúp tôi