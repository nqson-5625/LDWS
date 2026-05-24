{{ config(
    materialized='incremental',
    unique_key='event_id'
) }}

with alerts as (
    select * from {{ ref('staging_alert_events') }}
    {% if is_incremental() %}
        where load_timestamp > (select max(load_timestamp) from {{ this }})
    {% endif %}
),

-- Denormalize derived_features tại thời điểm trigger để lưu context cảnh báo
features as (
    select
        feature_id,
        station_id,
        timestamp,
        rain_1h,
        rain_24h,
        rain_3d,
        tilt_value,
        tilt_rate,
        disp_value,
        disp_rate,
        vibration_peak,
        risk_score
    from {{ ref('staging_derived_features') }}
),

-- Tính duration_min từ alert_status_snapshot
-- Khoảng thời gian trạm duy trì ở mức cảnh báo hiện tại
status_duration as (
    select
        station_id,
        latest_event_id,
        dbt_valid_from                              as alert_started_at,
        coalesce(dbt_valid_to, current_timestamp)   as alert_ended_at,
        datediff(
            'minute',
            dbt_valid_from,
            coalesce(dbt_valid_to, current_timestamp)
        )                                           as duration_min
    from {{ ref('alert_status_snapshot') }}
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
    a.event_id,

    -- FK dimensions
    d.date_key,
    st.station_key,
    a.alert_level,

    -- Degenerate dimensions
    a.area_id,
    a.station_id,

    -- Measures — context tại thời điểm cảnh báo
    a.risk_score,
    f.rain_1h,
    f.rain_24h,
    f.rain_3d,
    f.tilt_value,
    f.tilt_rate,
    f.disp_value,
    f.disp_rate,
    f.vibration_peak,

    -- Duration từ alert_status_snapshot
    sd.duration_min,
    sd.alert_started_at,

    -- Telegram audit
    a.telegram_sent,
    a.telegram_sent_at,
    datediff(
        'second',
        a.timestamp,
        a.telegram_sent_at
    )               as telegram_delay_sec,

    -- Metadata
    a.event_type,
    a.alert_message,
    a.timestamp     as event_timestamp,
    a.created_at,
    a.load_timestamp

from alerts a

-- Join derived_features tại thời điểm trigger
left join features f
    on  f.feature_id  = a.trigger_feature_id
    and f.station_id  = a.station_id
    and f.timestamp   = a.trigger_feature_timestamp

-- Join station SCD2
left join station_lookup st
    on  st.station_id = a.station_id
    and a.timestamp   >= st.effective_from
    and (a.timestamp  <  st.effective_to or st.effective_to is null)

-- Join date dimension
left join date_lookup d
    on  d.hour_timestamp = date_trunc('hour', a.timestamp)

-- Join duration từ snapshot
left join status_duration sd
    on  sd.station_id      = a.station_id
    and sd.latest_event_id = a.event_id
