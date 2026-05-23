{{ config(materialized='view') }}

select
    v:reading_id::bigint        as reading_id,
    v:timestamp::timestamp      as timestamp,
    v:area_id::bigint           as area_id,
    v:station_id::bigint        as station_id,
    v:sensor_id::bigint         as sensor_id,
    v:sensor_type::string       as sensor_type,
    v:value_1::float            as value_1,
    v:value_2::float            as value_2,
    v:value_3::float            as value_3,
    v:quality_flag::int         as quality_flag,
    v:created_at::timestamp     as created_at,
    current_timestamp           as load_timestamp
from {{ source('raw', 'sensor_readings') }}
where v:quality_flag::int not in (2, 3)   -- loại outlier và missing