from abc import ABC, abstractmethod


class PresenterAbstract(ABC):
    presenter = {}

    @classmethod
    @abstractmethod
    def get(cls):
        pass
