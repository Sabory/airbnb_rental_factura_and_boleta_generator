from abc import ABC, abstractmethod


class Presenter(ABC):
    @classmethod
    @abstractmethod
    def get(cls):
        pass