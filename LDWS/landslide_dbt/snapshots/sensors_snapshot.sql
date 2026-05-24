{% snapshot sensors_snapshot %}
{{
    config(
        target_schema='ANALYTICS',
        unique_key='sensor_id',
        strategy='check',
        check_cols=[
            'station_id',
            'type_code',
            'sensor_code',
            'sensor_name',
            'install_position',
            'status'
        ]
    )
}}

SELECT * FROM {{ ref('staging_sensors') }}

{% endsnapshot %}