from src.notifications.base import NotificationClient
import os

class SMSClient(NotificationClient):
    def __init__(self):
        self.api_key = os.getenv('SMS_API_KEY')

    def send(self, message: str, channel: str) -> bool:
        if not self.api_key:
            return False
        print(f"[SMS] Sent to {channel}: {message[:50]}...")
        return True

    def validate(self) -> bool:
        return bool(self.api_key)
