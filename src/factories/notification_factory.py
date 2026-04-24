from src.notifications.telegram import TelegramClient
from src.notifications.email import EmailClient
from src.notifications.sms import SMSClient

class UnsupportedChannelError(Exception):
    pass

def get_notification_client(channel: str):
    clients = {
        "telegram": TelegramClient,
        "email": EmailClient,
        "sms": SMSClient
    }
    if channel not in clients:
        raise UnsupportedChannelError(f"Channel '{channel}' not supported")
    return clients[channel]()
