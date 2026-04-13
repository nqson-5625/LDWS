import argparse

from app.db.session import SessionLocal
from app.services.user_service import UserService

def main():
    parser = argparse.ArgumentParser(description="Create a station admin account")
    parser.add_argument("--username", required=True, help="Station admin username")
    parser.add_argument("--password", required=True, help="Station admin password")

    parser.add_argument("--station-id", required=True, type=int, help="Assigned station ID")

    args = parser.parse_args()
    db = SessionLocal()

    try:
        service = UserService(db)
        user = service.create_station_admin(
            username=args.username,
            password=args.password,
            station_id=args.station_id
        )

        print(f"Created station_admin: username={user.username}, user_id={user.user_id}, station_id={user.station_id}")

    finally:
        db.close()

if __name__ == "__main__":
    main()