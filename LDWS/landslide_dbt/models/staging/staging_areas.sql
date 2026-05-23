{{ config(materialized='view') }}

with ranked as (
    select
        v:area_id::bigint           as area_id,
        v:area_name::string         as area_name,
        v:description::string       as description,
        v:latitude::float           as latitude,
        v:longitude::float          as longitude,
        v:status::string            as status,
        v:created_at::timestamp     as created_at,
        v:updated_at::timestamp     as updated_at,
        current_timestamp           as load_timestamp,
        row_number() over (
            partition by v:area_id::bigint
            order by v:updated_at::timestamp desc
        ) as rn
    from {{ source('raw', 'areas') }}
)

select
    area_id,
    area_name,
    description,
    latitude,
    longitude,
    status,
    created_at,
    updated_at,
    load_timestamp
from ranked
where rn = 1