from app.db.session import SessionLocal
from app.services.telegram_delivery_service import TelegramDeliveryService

# Gửi tất cả các cảnh báo đang chờ
def main():
    db = SessionLocal()
    try:
        service = TelegramDeliveryService(db)
        results = service.send_pending_events(limit=50)
        for item in results:
            print(item)
    finally:
        db.close()


if __name__ == "__main__":
    main()