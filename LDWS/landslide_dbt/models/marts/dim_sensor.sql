{{ config(materialized='table') }}

with source_data as (
    select
        dbt_scd_id      as sensor_key,
        sensor_id,
        station_id,
        type_code,
        sensor_code,
        sensor_name,
        install_position,
        status,
        created_at,
        dbt_valid_from  as effective_from,
        dbt_valid_to    as effective_to,
        case when dbt_valid_to is null then true else false
        end             as is_current
    from {{ ref('sensors_snapshot') }}
)

select * from source_data
