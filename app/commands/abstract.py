from abc import ABC, abstractmethod
import retry


class Command:
    @classmethod
    @retry(tries=2, delay=10, backoff=2)
    @abstractmethod
    def perform(self):
        pass
