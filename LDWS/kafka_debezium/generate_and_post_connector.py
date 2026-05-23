import json
import requests
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.core.config import settings


connector_config = {
    "name": "postgres-connector",
    "config": {
        "connector.class": "io.debezium.connector.postgresql.PostgresConnector",

        # Dùng internal host vì Debezium chạy trong Docker network
        "database.hostname": settings.internal_postgres_host,
        "database.port":     str(settings.internal_postgres_port),
        "database.user":     settings.postgres_user,
        "database.password": settings.postgres_password,
        "database.dbname":   settings.postgres_db,

        "topic.prefix":    "ldws_server",
        "plugin.name":     "pgoutput",
        "slot.name":       "ldws_slot",
        "publication.autocreate.mode":  "filtered",
        "tombstones.on.delete":         "false",
        "decimal.handling.mode":        "double",

        "table.include.list": ",".join([
            "public.areas",
            "public.stations",
            "public.sensors",
            "public.sensor_readings",
            "public.derived_features",
            "public.alert_events",
            "public.alert_status",
        ]),
    },
}

url = "http://localhost:8083/connectors"
headers = {"Content-Type": "application/json"}

response = requests.post(url, headers=headers, data=json.dumps(connector_config))

if response.status_code == 201:
    print("Connector created successfully!")
elif response.status_code == 409:
    print("Connector already exists.")
else:
    print(f"Failed to create connector ({response.status_code}): {response.text}")