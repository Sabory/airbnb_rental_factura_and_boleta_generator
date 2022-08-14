from abc import ABC, abstractmethod


class Command:
    @classmethod
    @abstractmethod
    def perform(self):
        pass
