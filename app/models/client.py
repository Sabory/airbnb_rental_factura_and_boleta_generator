from dataclasses import dataclass


@dataclass
class Client:
    name: str
    email: str

    @property
    def name_without_spaces(self):
        return self.name.replace(" ", "_")

    @property
    def has_email(self):
        return self.email != ""
