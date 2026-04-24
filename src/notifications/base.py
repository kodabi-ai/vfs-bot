from abc import ABC, abstractmethod

class NotificationClient(ABC):
    """Abstract base class for notification clients."""
    @abstractmethod
    def send(self, message: str, channel: str) -> bool:
        pass

    @abstractmethod
    def validate(self) -> bool:
        pass
