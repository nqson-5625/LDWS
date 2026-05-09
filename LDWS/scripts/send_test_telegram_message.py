import argparse

from app.integrations.telegram.bot_client import TelegramBotClient

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chat-id", required=True)
    parser.add_argument("--text", default="LDWS test message")
    args = parser.parse_args()

    client = TelegramBotClient()
    result = client.send_message(chat_id=args.chat_id, text=args.text)
    print(result)

if __name__ == "__main__":
    main()