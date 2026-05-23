create extension if not exists timescaledb;

-- Master Tables

create table if not exists areas (
	area_id bigserial primary key,
	area_name varchar(150) not null unique,
	description text,
	latitude double precision,
	longitude double precision,
	status varchar(20) not null default 'active',
	created_at timestamptz not null default now(),
	updated_at timestamptz not null default now(),
	
	constraint chk_areas_status check (status in ('active', 'inactive'))
);

create table if not exists stations (
	station_id bigserial primary key,
	area_id bigint not null,
	station_name varchar(150) not null,
	location_description text,
	latitude double precision,
	longitude double precision,
	elevation double precision,
	status varchar(20) not null default 'active',
	created_at timestamptz not null default now(),
	updated_at timestamptz not null default now(),
	
	constraint fk_stations_area foreign key (area_id) references areas(area_id) on delete cascade,
	constraint chk_stations_status check (status in ('active', 'inactive')),
	constraint uq_station_name_per_area unique (area_id, station_name)
);

create table if not exists users (
	user_id bigserial primary key,
	username varchar(150) not null unique,
	password_hash varchar(250) not null,
	role varchar(20) not null,
	station_id bigint, -- super_admin cos station_id = NULL
	is_active boolean default true,
	created_at timestamptz not null default now(),
	updated_at timestamptz not null default now(),
	
	constraint fk_user_station foreign key (station_id) references stations(station_id) on delete cascade,
	constraint chk_users_role check (role in ('super_admin', 'station_admin'))
);

create table if not exists sensor_types (
	type_code varchar(30) primary key,
	type_name varchar(100) not null,
	unit_1_name varchar(50),
	unit_1_symbol varchar(20),
	unit_2_name varchar(50),
	unit_2_symbol varchar(20),
	unit_3_name varchar(50),
	unit_3_symbol varchar(20),
	description text,
	created_at timestamptz not null default now()
);


create table if not exists sensors (
	sensor_id bigserial primary key,
	station_id bigint not null,
	type_code varchar(30) not null,
	sensor_code varchar(100) unique,
	sensor_name varchar(150) not null,
	install_position text,
	status varchar(20) not null default 'active',
	created_at timestamptz not null default now(),
	updated_at timestamptz not null default now(),
	
	constraint fk_sensors_station foreign key (station_id) references stations(station_id) on delete cascade,
	constraint fk_sensors_type foreign key (type_code) references sensor_types(type_code) on delete restrict,
	constraint chk_sensors_status check (status in ('active', 'inactive', 'maintenance'))
);

create table if not exists telegram_channels (
	channel_id bigserial primary key,
	area_id bigint not null unique,
	channel_name varchar(150) not null,
	telegram_chat_id varchar(100) not null unique,
	channel_link text,
	qr_code_url text,
	is_active boolean not null default true,
	created_at timestamptz not null default now(),
	updated_at timestamptz not null default now(),
	
	constraint fk_telegram_channels_area foreign key (area_id) references areas(area_id) on delete cascade
);

-- Dữ liệu thô time-series (HyperTable)

create table if not exists sensor_readings (
	reading_id  bigserial,
	"timestamp" timestamptz not null,
	area_id bigint not null,
	station_id bigint not null,
	sensor_id bigint not null,
	sensor_type varchar(30) not null, 
	value_1 double precision,
	value_2 double precision,
	value_3 double precision,
	quality_flag smallint not null default 0,
	-- Quality_flag: 0 = good, 1 = suspect, 2 = outlier, 3 = missing, 4 = interpolated

	raw_payload jsonb,
	created_at timestamptz not null default now(),
	
	constraint pk_sensor_readings primary key (reading_id, "timestamp"),
	constraint fk_sensor_readings_area foreign key (area_id) references areas(area_id) on delete cascade,
	constraint fk_sensor_readings_station foreign key (station_id) references stations(station_id) on delete cascade,
	constraint fk_sensor_readings_sensor foreign key (sensor_id) references sensors(sensor_id) on delete cascade,
	constraint fk_sensor_readings_type foreign key (sensor_type) references sensor_types(type_code) on delete restrict,
	constraint chk_sensor_readings_quality_flag check (quality_flag in (0, 1, 2, 3, 4))
);

select create_hypertable('sensor_readings', 'timestamp', if_not_exists => true);

-- Đặc trưng dẫn xuất (HyperTable)

create table if not exists derived_features (
	feature_id bigserial,
	"timestamp" timestamptz not null,
	area_id bigint not null,
	station_id bigint not null,
	
	rain_1h double precision,
	rain_3h double precision,
	rain_24h double precision,
	rain_3d double precision,
	rain_intensity double precision,
	
	tilt_value double precision,
	tilt_rate double precision,
	tilt_change_1h double precision,
	tilt_change_24h double precision,
	
	disp_value double precision,
	disp_rate double precision,
	disp_change_1h double precision,
	disp_change_24h double precision,
	
	vibration_value double precision,
	vibration_peak double precision,
	vibration_flag boolean default false,
	
	temperature_value double precision,
	temperature_flag boolean default false,
	
	anomaly_score double precision,
	anomaly_flag boolean not null default false,
	
	risk_score double precision,
	alert_level_candidate smallint,
	created_at timestamptz not null default now(),
	
	constraint pk_derived_features primary key (feature_id, "timestamp"),
	constraint fk_derived_features_area foreign key (area_id) references areas(area_id) on delete cascade,
	constraint fk_derived_features_station foreign key (station_id) references stations(station_id) on delete cascade,
	constraint chk_derived_features_alert_level check (alert_level_candidate is null or alert_level_candidate in (1, 2, 3, 4, 5))
);

ALTER TABLE derived_features
ADD CONSTRAINT uq_derived_features_station_time
UNIQUE (station_id, "timestamp");

select create_hypertable('derived_features', 'timestamp', if_not_exists => true);

-- Các cấp cảnh báo

create table if not exists alert_levels (
	alert_level smallint primary key,
	alert_name varchar(50) not null unique,
	alert_color varchar(30) not null,
	description text
);


-- Các sự kiện cảnh báo (HyperTable)

create table if not exists alert_events (
	event_id bigserial,
	"timestamp" timestamptz not null,
	area_id bigint not null,
	station_id bigint not null,
	alert_level smallint not null,
	risk_score double precision,
	
	-- tham chiếu mềm đến derived_features gây ra cảnh báo
	trigger_feature_id bigint,
	trigger_feature_timestamp timestamptz,
	
	alert_message text,
	event_type varchar(20) not null,
	telegram_sent boolean not null default false,
	telegram_sent_at timestamptz,
	created_at timestamptz not null default now(),
	
	constraint pk_alert_events primary key (event_id, "timestamp"),
	constraint fk_alert_events_area foreign key (area_id) references areas(area_id) on delete cascade,
	constraint fk_alert_events_station foreign key (station_id) references stations(station_id) on delete cascade,
	constraint fk_alert_events_level foreign key (alert_level) references alert_levels(alert_level),
	constraint chk_alert_event_type check (event_type in ('created', 'upgraded', 'downgraded', 'resolved'))
);

select create_hypertable('alert_events', 'timestamp', if_not_exists => true);

-- Trạng thái cảnh báo của từng trạm đo

create table if not exists alert_status (
	station_id bigint primary key,
	latest_event_id bigint not null,
	latest_event_timestamp timestamptz not null,
	updated_at timestamptz not null default now(),
	
	constraint fk_alert_status_station foreign key (station_id) references stations(station_id) on delete cascade,
	constraint fk_alert_status_event
		foreign key (latest_event_id, latest_event_timestamp)
		references alert_events(event_id, "timestamp") on delete cascade
);

-- Đánh chỉ mục cho FK

create index if not exists idx_stations_area_id on stations(area_id);
create index if not exists idx_sensors_station_id on sensors(station_id);
create index if not exists idx_sensors_type_code on sensors(type_code);

-- Đánh chỉ mục kết hợp

create index if not exists idx_sensor_readings_station_time on sensor_readings(station_id, "timestamp" DESC);
create index if not exists idx_sensor_readings_area_time on sensor_readings(area_id, "timestamp" DESC);
create index if not exists idx_sensor_readings_sensor_time on sensor_readings(sensor_id, "timestamp" DESC);
create index if not exists idx_sensor_readings_type_time on sensor_readings(sensor_type, "timestamp" DESC);

create index if not exists idx_derived_features_area_time on derived_features(area_id, "timestamp" DESC);
create index if not exists idx_derived_features_station_time on derived_features(station_id, "timestamp" DESC);

create index if not exists idx_alert_events_area_time on alert_events(area_id, "timestamp" DESC);
create index if not exists idx_alert_events_station_time on alert_events(station_id, "timestamp" DESC);

create unique index if not exists idx_alert_status_latest_event on alert_status(latest_event_id, latest_event_timestamp);

-- Hàm tự động cập nhật thời gian
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Gắn Trigger cho bảng areas
CREATE OR REPLACE TRIGGER trg_areas_updated_at
BEFORE UPDATE ON areas
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Gắn Trigger cho bảng stations
CREATE OR REPLACE TRIGGER trg_stations_updated_at
BEFORE UPDATE ON stations
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Gắn Trigger cho bảng users
CREATE OR REPLACE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Gắn Trigger cho bảng sensors
CREATE OR REPLACE TRIGGER trg_sensors_updated_at
BEFORE UPDATE ON sensors
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Gắn Trigger cho bảng telegram_channels
CREATE OR REPLACE TRIGGER trg_telegram_channels_updated_at
BEFORE UPDATE ON telegram_channels
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Gắn Trigger cho bảng alert_status
CREATE OR REPLACE TRIGGER trg_alert_status_updated_at
BEFORE UPDATE ON alert_status
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Kích hoạt và cấu hình Compression cho bảng sensor_readings

alter table sensor_readings set (
	timescaledb.compress = true,
	-- Gom tất cả các dòng dữ liệu có cùng station_id và sensor_type vào 1 segment để nén
	timescaledb.compress_segmentby = 'station_id, sensor_type', 
	-- Bên trong các segment đã gom, sắp xếp thời gian giảm dần
	timescaledb.compress_orderby = '"timestamp" DESC'
);

-- Tự động hóa quá trình nén

select add_compression_policy (
	'sensor_readings',
	compress_after => interval '30 days', -- KHÔNG nén dữ liệu trong vòng 30 days
	if_not_exists => true
);

-- Tự động hóa quá trình dọn rác

select add_retention_policy (
	'sensor_readings',
	drop_after => interval '2 years', -- XÓA những dữ liệu cũ hơn 2 years
	if_not_exists => true
);

-- Kích hoạt và cấu hình Compression cho bảng derived_features

alter table derived_features set (
	timescaledb.compress = true,
	-- Gom tất cả các dòng dữ liệu có cùng station_id vào 1 segment để nén
	timescaledb.compress_segmentby = 'station_id', 
	-- Bên trong các segment đã gom, sắp xếp thời gian giảm dần
	timescaledb.compress_orderby = '"timestamp" DESC'
);

-- Tự động hóa quá trình nén

select add_compression_policy (
	'derived_features',
	compress_after => interval '30 days', -- KHÔNG nén dữ liệu trong vòng 30 days
	if_not_exists => true
);

