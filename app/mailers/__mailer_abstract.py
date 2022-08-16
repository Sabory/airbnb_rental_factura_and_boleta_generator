from abc import ABC, abstractmethod
from core.mailer import Mailer


class MailerAbstract(ABC):
    @classmethod
    @abstractmethod
    def perform(cls):
        pass

    @classmethod
    def send(cls, presenter):
        Mailer.send_email(
            email_to=presenter["email_to"],
            subject=presenter["subject"],
            content=presenter.get["content"],
            attachments=presenter.get("attachments", None),
        )
