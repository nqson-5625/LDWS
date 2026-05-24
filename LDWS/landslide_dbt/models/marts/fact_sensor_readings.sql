{{ config(
    materialized='incremental',
    unique_key='reading_id'
) }}

with readings as (
    select * from {{ ref('staging_sensor_readings') }}
    {% if is_incremental() %}
        where load_timestamp > (select max(load_timestamp) from {{ this }})
    {% endif %}
),

-- Lookup station_key: lấy version SCD2 hiệu lực tại thời điểm đo
station_lookup as (
    select station_key, station_id, effective_from, effective_to
    from {{ ref('dim_station') }}
),

-- Lookup sensor_key: lấy version SCD2 hiệu lực tại thời điểm đo
sensor_lookup as (
    select sensor_key, sensor_id, effective_from, effective_to
    from {{ ref('dim_sensor') }}
),

-- Lookup date_key theo giờ
date_lookup as (
    select date_key, hour_timestamp
    from {{ ref('dim_date') }}
)

select
    r.reading_id,

    -- FK dimensions
    d.date_key,
    st.station_key,
    se.sensor_key,

    -- Degenerate dimensions (giữ lại để filter nhanh, không cần join)
    r.area_id,
    r.station_id,
    r.sensor_id,
    r.sensor_type,

    -- Measures
    r.value_1,
    r.value_2,
    r.value_3,
    r.quality_flag,

    -- Audit
    r.timestamp     as reading_timestamp,
    r.created_at,
    r.load_timestamp

from readings r

-- Join station SCD2: lấy đúng version tại thời điểm đo
left join station_lookup st
    on  st.station_id    = r.station_id
    and r.timestamp      >= st.effective_from
    and (r.timestamp     <  st.effective_to or st.effective_to is null)

-- Join sensor SCD2: lấy đúng version tại thời điểm đo
left join sensor_lookup se
    on  se.sensor_id     = r.sensor_id
    and r.timestamp      >= se.effective_from
    and (r.timestamp     <  se.effective_to or se.effective_to is null)

-- Join date dimension theo giờ
left join date_lookup d
    on  d.hour_timestamp = date_trunc('hour', r.timestamp)
