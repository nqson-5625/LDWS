{% snapshot alert_status_snapshot %}
{{
    config(
        target_schema='ANALYTICS',
        unique_key='station_id',
        strategy='check',
        check_cols=[
            'latest_event_id',
            'latest_event_timestamp'
        ]
    )
}}

SELECT * FROM {{ ref('staging_alert_status') }}

{% endsnapshot %}