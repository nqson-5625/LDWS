{{ config(materialized='view') }}

with ranked as (
    select
        v:station_id::bigint                    as station_id,
        v:latest_event_id::bigint               as latest_event_id,
        v:latest_event_timestamp::timestamp     as latest_event_timestamp,
        v:updated_at::timestamp                 as updated_at,
        current_timestamp                       as load_timestamp,
        row_number() over (
            partition by v:station_id::bigint
            order by v:updated_at::timestamp desc
        ) as rn
    from {{ source('raw', 'alert_status') }}
)

select
    station_id,
    latest_event_id,
    latest_event_timestamp,
    updated_at,
    load_timestamp
from ranked
where rn = 1