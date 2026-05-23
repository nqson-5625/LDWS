{{ config(materialized='view') }}

select
    v:event_id::bigint                      as event_id,
    v:timestamp::timestamp                  as timestamp,
    v:area_id::bigint                       as area_id,
    v:station_id::bigint                    as station_id,
    v:alert_level::int                      as alert_level,
    v:risk_score::float                     as risk_score,
    v:trigger_feature_id::bigint            as trigger_feature_id,
    v:trigger_feature_timestamp::timestamp  as trigger_feature_timestamp,
    v:alert_message::string                 as alert_message,
    v:event_type::string                    as event_type,
    v:telegram_sent::boolean                as telegram_sent,
    v:telegram_sent_at::timestamp           as telegram_sent_at,
    v:created_at::timestamp                 as created_at,
    current_timestamp                       as load_timestamp
from {{ source('raw', 'alert_events') }}