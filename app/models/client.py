from dataclasses import dataclass


@dataclass
class Client:
    name: str
    email: str

    @property
    def name_without_spaces(self):
        return self.name.replace(" ", "_")
