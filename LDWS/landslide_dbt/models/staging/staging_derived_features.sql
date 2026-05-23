{{ config(materialized='view') }}

select
    v:feature_id::bigint            as feature_id,
    v:timestamp::timestamp          as timestamp,
    v:area_id::bigint               as area_id,
    v:station_id::bigint            as station_id,

    -- Rain
    v:rain_1h::float                as rain_1h,
    v:rain_3h::float                as rain_3h,
    v:rain_24h::float               as rain_24h,
    v:rain_3d::float                as rain_3d,
    v:rain_intensity::float         as rain_intensity,

    -- Tilt
    v:tilt_value::float             as tilt_value,
    v:tilt_rate::float              as tilt_rate,
    v:tilt_change_1h::float         as tilt_change_1h,
    v:tilt_change_24h::float        as tilt_change_24h,

    -- Displacement
    v:disp_value::float             as disp_value,
    v:disp_rate::float              as disp_rate,
    v:disp_change_1h::float         as disp_change_1h,
    v:disp_change_24h::float        as disp_change_24h,

    -- Vibration
    v:vibration_value::float        as vibration_value,
    v:vibration_peak::float         as vibration_peak,
    v:vibration_flag::boolean       as vibration_flag,

    -- Temperature
    v:temperature_value::float      as temperature_value,
    v:temperature_flag::boolean     as temperature_flag,

    -- Anomaly & Risk
    v:anomaly_score::float          as anomaly_score,
    v:anomaly_flag::boolean         as anomaly_flag,
    v:risk_score::float             as risk_score,
    v:alert_level_candidate::int    as alert_level_candidate,

    v:created_at::timestamp         as created_at,
    current_timestamp               as load_timestamp
from {{ source('raw', 'derived_features') }}