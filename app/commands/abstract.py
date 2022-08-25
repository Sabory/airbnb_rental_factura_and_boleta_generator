from abc import ABC, abstractmethod
from retry import retry


class CommandAbstract:
    @classmethod
    @retry(tries=2, delay=10, backoff=2)
    @abstractmethod
    def perform(self):
        pass
