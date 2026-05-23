insert into sensor_types (
	type_code, type_name,
	unit_1_name, unit_1_symbol,
	unit_2_name, unit_2_symbol,
	unit_3_name, unit_3_symbol
)
values 
	('rain', 'Cảm biến lượng mưa', 'Lượng mưa', 'mm', NULL, NULL, NULL, NULL),
    ('tilt', 'Cảm biến độ nghiêng', 'Trục X', 'độ', 'Trục Y', 'độ', NULL, NULL),
    ('vibration', 'Cảm biến độ rung', 'Gia tốc X', 'g', 'Gia tốc Y', 'g', 'Gia tốc Z', 'g'),
    ('displacement', 'Cảm biến dịch chuyển', 'Độ dời', 'mm', NULL, NULL, NULL, NULL),
    ('temperature', 'Cảm biến nhiệt độ', 'Nhiệt độ', '°C', NULL, NULL, NULL, NULL)
ON CONFLICT (type_code) DO NOTHING; -- Nếu UpSert mà conflict thì sẽ do nothing (không làm gì cả)


insert into alert_levels
values 
	(1, 'Rất thấp', 'blue', 'Trạng thái ổn định, nguy cơ rất thấp'),
    (2, 'Thấp', 'green', 'Có dấu hiệu nhẹ, cần theo dõi'),
    (3, 'Trung bình', 'yellow', 'Nguy cơ trung bình, cần giám sát chặt'),
    (4, 'Cao', 'red', 'Nguy cơ cao, cần phát cảnh báo'),
    (5, 'Rất cao', 'purple', 'Nguy cơ rất cao, cần cảnh báo khẩn')
ON CONFLICT (alert_level) DO NOTHING;


-- Insert sensors for NOIBAI INTL station

-- rain × 1 
INSERT INTO sensors (station_id, type_code, sensor_code, sensor_name, install_position, status)
VALUES
    (1, 'rain', 'HN-NBI-RAIN-01',
     'Cảm biến lượng mưa trạm Nội Bài',
     'Mái nhà trạm quan trắc, hướng Bắc, cao 3 m so với mặt đất',
     'active');

-- tilt × 2
INSERT INTO sensors (station_id, type_code, sensor_code, sensor_name, install_position, status)
VALUES
    (1, 'tilt', 'HN-NBI-TILT-01',
     'Cảm biến độ nghiêng trạm Nội Bài - Mặt cắt A',
     'Đỉnh ta-luy phía Đông đường băng, sâu 0.5 m dưới mặt đất',
     'active'),
    (1, 'tilt', 'HN-NBI-TILT-02',
     'Cảm biến độ nghiêng trạm Nội Bài - Mặt cắt B',
     'Chân ta-luy phía Đông đường băng, sâu 0.3 m dưới mặt đất',
     'active');

-- vibration × 2 
INSERT INTO sensors (station_id, type_code, sensor_code, sensor_name, install_position, status)
VALUES
    (1, 'vibration', 'HN-NBI-VIB-01',
     'Cảm biến rung trạm Nội Bài - Gần chân mái',
     'Chân mái dốc phía Đông, cách mép đường 5 m, gắn trên cọc bê-tông',
     'active'),
    (1, 'vibration', 'HN-NBI-VIB-02',
     'Cảm biến rung trạm Nội Bài - Đối chứng',
     'Khu vực ổn định phía Tây, cách mái dốc 50 m, dùng để đối chiếu nền',
     'active');

-- displacement × 3 
INSERT INTO sensors (station_id, type_code, sensor_code, sensor_name, install_position, status)
VALUES
    (1, 'displacement', 'HN-NBI-DISP-01',
     'Cảm biến dịch chuyển trạm Nội Bài - Điểm neo P1',
     'Đỉnh mái dốc, điểm neo P1 (cọc mốc số 1), đo chuyển vị ngang',
     'active'),
    (1, 'displacement', 'HN-NBI-DISP-02',
     'Cảm biến dịch chuyển trạm Nội Bài - Điểm neo P2',
     'Giữa mái dốc, điểm neo P2 (cọc mốc số 2), đo chuyển vị ngang',
     'active'),
    (1, 'displacement', 'HN-NBI-DISP-03',
     'Cảm biến dịch chuyển trạm Nội Bài - Điểm neo P3',
     'Chân mái dốc, điểm neo P3 (cọc mốc số 3), đo chuyển vị ngang',
     'active');

-- temperature × 1
INSERT INTO sensors (station_id, type_code, sensor_code, sensor_name, install_position, status)
VALUES
    (1, 'temperature', 'HN-NBI-TEMP-01',
     'Cảm biến nhiệt độ trạm Nội Bài',
     'Lều khí tượng tiêu chuẩn, cao 1.5 m, che bức xạ mặt trời',
     'active');


-- Insert sensors for HA DONG station

-- rain × 1 
INSERT INTO sensors (station_id, type_code, sensor_code, sensor_name, install_position, status)
VALUES
    (2, 'rain', 'HN-HDG-RAIN-01',
     'Cảm biến lượng mưa trạm Hà Đông',
     'Mái trạm quan trắc Hà Đông, cao 3 m so với mặt đất',
     'active');

-- tilt × 2 
INSERT INTO sensors (station_id, type_code, sensor_code, sensor_name, install_position, status)
VALUES
    (2, 'tilt', 'HN-HDG-TILT-01',
     'Cảm biến độ nghiêng trạm Hà Đông - Mặt cắt A',
     'Đỉnh bờ kè sông Nhuệ, phía thượng lưu, sâu 0.5 m',
     'active'),
    (2, 'tilt', 'HN-HDG-TILT-02',
     'Cảm biến độ nghiêng trạm Hà Đông - Mặt cắt B',
     'Chân bờ kè sông Nhuệ, phía hạ lưu, sâu 0.3 m',
     'active');

-- vibration × 2 
INSERT INTO sensors (station_id, type_code, sensor_code, sensor_name, install_position, status)
VALUES
    (2, 'vibration', 'HN-HDG-VIB-01',
     'Cảm biến rung trạm Hà Đông - Gần bờ kè',
     'Chân bờ kè, cách mép nước 3 m, gắn trên cọc thép',
     'active'),
    (2, 'vibration', 'HN-HDG-VIB-02',
     'Cảm biến rung trạm Hà Đông - Đối chứng',
     'Nền ổn định cách bờ kè 60 m, dùng để lọc nhiễu giao thông đô thị',
     'active');

-- displacement × 3 
INSERT INTO sensors (station_id, type_code, sensor_code, sensor_name, install_position, status)
VALUES
    (2, 'displacement', 'HN-HDG-DISP-01',
     'Cảm biến dịch chuyển trạm Hà Đông - Điểm neo P1',
     'Đỉnh bờ kè, cọc mốc P1, đo dịch chuyển hướng ra sông',
     'active'),
    (2, 'displacement', 'HN-HDG-DISP-02',
     'Cảm biến dịch chuyển trạm Hà Đông - Điểm neo P2',
     'Giữa taluy bờ kè, cọc mốc P2, đo dịch chuyển hướng ra sông',
     'active'),
    (2, 'displacement', 'HN-HDG-DISP-03',
     'Cảm biến dịch chuyển trạm Hà Đông - Điểm neo P3',
     'Chân bờ kè, cọc mốc P3, đo dịch chuyển hướng ra sông',
     'active');

-- temperature × 1 
INSERT INTO sensors (station_id, type_code, sensor_code, sensor_name, install_position, status)
VALUES
    (2, 'temperature', 'HN-HDG-TEMP-01',
     'Cảm biến nhiệt độ trạm Hà Đông',
     'Lều khí tượng tiêu chuẩn gần bờ kè, cao 1.5 m',
     'active');


SELECT
    s.sensor_id,
    st.station_name,
    s.type_code,
    s.sensor_code,
    s.sensor_name,
    s.status
FROM sensors s
JOIN stations st ON st.station_id = s.station_id
WHERE st.area_id = 4
ORDER BY st.station_id, s.type_code, s.sensor_id;