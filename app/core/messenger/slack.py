from .abstract import Messenger
import os
from dotenv import load_dotenv
import requests
from retry import retry

load_dotenv()


class Slack(Messenger):
    CHANNELS = {
        "casona": os.getenv("SLACK_WEBHOOK_CASONA"),
        "boletas": os.getenv("SLACK_WEBHOOK_URL_BOLETAS_GEN"),
    }

    @classmethod
    def send_message(cls, message, channel="boletas"):
        data = {
            "text": message,
        }
        url = cls.__get_channel_webhook(channel)

        try:
            cls.__send(url, data)
        except requests.exceptions.SSLError:
            return None

    @classmethod
    def __get_channel_webhook(cls, channel):
        return cls.CHANNELS[channel]

    @retry(requests.exceptions.SSLError, tries=3, delay=10, backoff=2)
    def __send(url, data):
        res = requests.post(url, json=data)
