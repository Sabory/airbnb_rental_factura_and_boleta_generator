import smtplib
from email.message import EmailMessage

from config import config
from os import path


class Mailer:
    SENDER_ADDRESS = config["mailer"]["email"].get(str)
    SENDER_PASSWORD = config["mailer"]["password"].get(str)
    DEFAULT_BCCS = config["mailer"]["default_bcc"].get(list)
    MAILER_SMTP = config["mailer"]["smtp_server"].get(list)

    @classmethod
    def send_email(
        cls, email_to: str, subject: str, content: str, attachments: list = None
    ) -> None:
        message = EmailMessage()
        message["From"] = cls.SENDER_ADDRESS
        message["To"] = email_to
        message["Bcc"] = cls.DEFAULT_BCCS
        message["Subject"] = subject

        message.set_content(content)

        if attachments:
            message = cls._attach_files(message, attachments)

        with smtplib.SMTP(*cls.MAILER_SMTP) as session:
            session.starttls()
            session.login(cls.SENDER_ADDRESS, cls.SENDER_PASSWORD)
            session.send_message(message)
            print("Mail Sent")

    def _attach_files(message: EmailMessage, attachments: list = None) -> None:
        for attachment in attachments:
            with open(attachment, "rb") as f:
                message.add_attachment(
                    f.read(),
                    maintype="application",
                    subtype="octet-stream",
                    filename=path.basename(attachment),
                )
        return message
