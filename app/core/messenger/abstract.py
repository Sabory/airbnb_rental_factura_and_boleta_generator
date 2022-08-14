from abc import ABC, abstractmethod


class Messenger(ABC):
    @property
    @abstractmethod
    def webhook_url(self):
        pass

    @abstractmethod
    def send_message(self, message):
        pass
