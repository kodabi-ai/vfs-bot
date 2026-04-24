from src.notifications.base import NotificationClient
import os

class EmailClient(NotificationClient):
    def __init__(self):
        self.smtp_host = os.getenv('EMAIL_SMTP_HOST')
        self.sender = os.getenv('EMAIL_SENDER')
        self.password = os.getenv('EMAIL_PASSWORD')

    def send(self, message: str, channel: str) -> bool:
        if not all([self.smtp_host, self.sender, self.password]):
            return False
        print(f"[Email] Sent to {channel}: {message[:50]}...")
        return True

    def validate(self) -> bool:
        return bool(self.smtp_host and self.sender and self.password)
