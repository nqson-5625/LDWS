{{ config(materialized='table') }}

with source_data as (
    select
        dbt_scd_id      as station_key,
        station_id,
        area_id,
        station_name,
        location_description,
        latitude,
        longitude,
        elevation,
        status,
        created_at,
        dbt_valid_from  as effective_from,
        dbt_valid_to    as effective_to,
        case when dbt_valid_to is null then true else false
        end             as is_current
    from {{ ref('stations_snapshot') }}
)

select * from source_data
