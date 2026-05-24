# docker/dags/scd_snapshots_dag.py
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="scd_snapshots_landslide",
    default_args=default_args,
    description="Run dbt snapshots (SCD2) và dbt run marts cho landslide",
    schedule_interval="@hourly",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["dbt", "snapshots", "landslide"],
) as dag:

    # Chạy snapshot cho stations, sensors, alert_status
    dbt_snapshot = BashOperator(
        task_id="dbt_snapshot",
        bash_command=(
            "cd /opt/airflow/landslide_dbt && "
            "dbt snapshot --profiles-dir /home/airflow/.dbt"
        ),
    )

    # Chạy marts sau khi snapshot hoàn thành
    # Marts phụ thuộc vào snapshot (dim_stations, dim_sensors, dim_alert_status dùng SCD2 data)
    dbt_run_marts = BashOperator(
        task_id="dbt_run_marts",
        bash_command=(
            "cd /opt/airflow/landslide_dbt && "
            "dbt run --select marts --profiles-dir /home/airflow/.dbt"
        ),
    )

    dbt_snapshot >> dbt_run_marts
