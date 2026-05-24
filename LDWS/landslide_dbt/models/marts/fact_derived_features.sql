{{ config(
    materialized='incremental',
    unique_key='feature_id'
) }}

with features as (
    select * from {{ ref('staging_derived_features') }}
    {% if is_incremental() %}
        where load_timestamp > (select max(load_timestamp) from {{ this }})
    {% endif %}
),

station_lookup as (
    select station_key, station_id, effective_from, effective_to
    from {{ ref('dim_station') }}
),

date_lookup as (
    select date_key, hour_timestamp
    from {{ ref('dim_date') }}
)

select
    f.feature_id,

    -- FK dimensions
    d.date_key,
    st.station_key,

    -- Degenerate dimensions
    f.area_id,
    f.station_id,

    -- Rain measures
    f.rain_1h,
    f.rain_3h,
    f.rain_24h,
    f.rain_3d,
    f.rain_intensity,

    -- Tilt measures
    f.tilt_value,
    f.tilt_rate,
    f.tilt_change_1h,
    f.tilt_change_24h,

    -- Displacement measures
    f.disp_value,
    f.disp_rate,
    f.disp_change_1h,
    f.disp_change_24h,

    -- Vibration measures
    f.vibration_value,
    f.vibration_peak,
    f.vibration_flag,

    -- Temperature measures
    f.temperature_value,
    f.temperature_flag,

    -- Risk indicators
    f.anomaly_score,
    f.anomaly_flag,
    f.risk_score,
    f.alert_level_candidate,

    -- Audit
    f.timestamp     as feature_timestamp,
    f.created_at,
    f.load_timestamp

from features f

left join station_lookup st
    on  st.station_id = f.station_id
    and f.timestamp   >= st.effective_from
    and (f.timestamp  <  st.effective_to or st.effective_to is null)

left join date_lookup d
    on  d.hour_timestamp = date_trunc('hour', f.timestamp)
