from abc import ABC, abstractmethod

from dataclasses import dataclass, field


@dataclass
class Document(ABC):
    id: str
    file_name: str
    with_taxes: bool
    url: str = field(repr=False)
    path: str = field(init=False, repr=False)

    @classmethod
    @abstractmethod
    def generate_document(cls):
        """Main & complete fuction to generate a boleta.
        file_name: str -> name of the file for the downloaded boleta
        interactive: bool -> if True, will stop and ask for confirmation
                            in every important part
        """
        pass
