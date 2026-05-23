{{ config(materialized='view') }}

with ranked as (
    select
        v:station_id::bigint            as station_id,
        v:area_id::bigint               as area_id,
        v:station_name::string          as station_name,
        v:location_description::string  as location_description,
        v:latitude::float               as latitude,
        v:longitude::float              as longitude,
        v:elevation::float              as elevation,
        v:status::string                as status,
        v:created_at::timestamp         as created_at,
        v:updated_at::timestamp         as updated_at,
        current_timestamp               as load_timestamp,
        row_number() over (
            partition by v:station_id::bigint
            order by v:updated_at::timestamp desc
        ) as rn
    from {{ source('raw', 'stations') }}
)

select
    station_id,
    area_id,
    station_name,
    location_description,
    latitude,
    longitude,
    elevation,
    status,
    created_at,
    updated_at,
    load_timestamp
from ranked
where rn = 1