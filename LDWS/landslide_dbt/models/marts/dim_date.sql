{{ config(materialized='table') }}

with hours as (
    select
        dateadd('hour', seq4(), '2025-01-01 00:00:00'::timestamp) as hour_ts
    from table(generator(rowcount => 87600))  -- 10 năm × 8760 giờ/năm
)

select
    to_number(to_char(hour_ts, 'YYYYMMDDHH24'))      as date_key,
    hour_ts                                          as hour_timestamp,
    date_trunc('day',  hour_ts)::date                as date,
    date_trunc('month', hour_ts)::date               as month_date,
    year(hour_ts)                                    as year,
    month(hour_ts)                                   as month,
    day(hour_ts)                                     as day,
    hour(hour_ts)                                    as hour,
    dayofweek(hour_ts)                               as day_of_week,
    dayname(hour_ts)                                 as day_name,
    monthname(hour_ts)                               as month_name,
    quarter(hour_ts)                                 as quarter,
    -- Phân loại giờ trong ngày phục vụ phân tích mưa/nhiệt độ
    case
        when hour(hour_ts) between 6  and 11 then 'Sáng'
        when hour(hour_ts) between 12 and 17 then 'Chiều'
        when hour(hour_ts) between 18 and 21 then 'Tối'
        else 'Đêm'
    end                                              as time_of_day,
    -- Phân loại mùa (khí hậu miền Bắc Việt Nam)
    case
        when month(hour_ts) between 5 and 10 then 'Mùa mưa'
        else 'Mùa khô'
    end                                              as season
from hours
