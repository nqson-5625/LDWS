import argparse # Đọc tham số từ Terminal

from app.db.session import SessionLocal
from app.services.user_service import UserService

def main():
    # Cấu hình công cụ đọc tham số dòng lệnh
    parser = argparse.ArgumentParser(description="Create a super admin account")

    parser.add_argument("--username", required=True, help="Super admin username")
    parser.add_argument("--password", required=True, help="Super admin password")

    # Đọc và phân tích lệnh gõ trên Terminal
    args = parser.parse_args()
    # Mở kết nối trực tiếp đến db không thông qua API
    db = SessionLocal()

    try:
        service = UserService(db)
        user = service.create_super_admin(
            username=args.username,
            password=args.password
        )
        print(f"Created super_admin: username={user.username}, user_id={user.user_id}")

    finally:
        db.close()

if __name__ == "__main__":
    main()