{% snapshot stations_snapshot %}
{{
    config(
        target_schema='ANALYTICS',
        unique_key='station_id',
        strategy='check',
        check_cols=[
            'station_name',
            'location_description',
            'latitude',
            'longitude',
            'elevation',
            'status'
        ]
    )
}}

SELECT * FROM {{ ref('staging_stations') }}

{% endsnapshot %}