{{ config(materialized='view') }}

with ranked as (
    select
        v:sensor_id::bigint         as sensor_id,
        v:station_id::bigint        as station_id,
        v:type_code::string         as type_code,
        v:sensor_code::string       as sensor_code,
        v:sensor_name::string       as sensor_name,
        v:install_position::string  as install_position,
        v:status::string            as status,
        v:created_at::timestamp     as created_at,
        v:updated_at::timestamp     as updated_at,
        current_timestamp           as load_timestamp,
        row_number() over (
            partition by v:sensor_id::bigint
            order by v:updated_at::timestamp desc
        ) as rn
    from {{ source('raw', 'sensors') }}
)

select
    sensor_id,
    station_id,
    type_code,
    sensor_code,
    sensor_name,
    install_position,
    status,
    created_at,
    updated_at,
    load_timestamp
from ranked
where rn = 1