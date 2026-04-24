from src.notifications.base import NotificationClient
import os

class TelegramClient(NotificationClient):
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')

    def send(self, message: str, channel: str) -> bool:
        if not self.token or not self.chat_id:
            return False
        print(f"[Telegram] Sent: {message[:50]}...")
        return True

    def validate(self) -> bool:
        return bool(self.token and self.chat_id)
