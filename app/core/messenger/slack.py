from .abstract import Messenger

from config import config
import requests
from retry import retry


class Slack(Messenger):
    CHANNELS = {
        "casona": config["slack"]["channels"]["casona"],
        "boletas": config["slack"]["channels"]["boletas"],
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
