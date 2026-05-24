{{ config(materialized='table') }}

select  1                               as alert_level, 
        'Bình thường'                   as level_name, 
        '#2ECC71'                     as color_code,
        'Không có dấu hiệu nguy hiểm'   as description,
        0.0                             as risk_threshold
union all
select  2                               as alert_level,
        'Theo dõi'                      as level_name,
        '#F1C40F'                     as color_code,
        'Có dấu hiệu bất thường, cần theo dõi thêm' as description,
        0.3                             as risk_threshold
union all
select  3                               as alert_level,
        'Cảnh báo'                      as level_name,
        '#E67E22'                     as color_code,
        'Nguy cơ sạt lở, khuyến cáo sơ tán'   as description,
        0.5                             as risk_threshold
union all
select  4                               as alert_level,
        'Nguy hiểm'                      as level_name,
        '#E74C3C'                     as color_code,
        'Nguy cơ cao, bắt buộc sơ tán'   as description,
        0.7                             as risk_threshold
union all
select  5                               as alert_level,
        'Rất nguy hiểm'                 as level_name,
        '#8E1A1A'                     as color_code,
        'Sạt lở đang xảy ra hoặc sắp xảy ra'   as description,
        0.9                             as risk_threshold
