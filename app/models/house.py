from dataclasses import dataclass

from config import config


@dataclass(eq=True)
class House:
    name: str
    price_per_night: float
    cleaning_fee: float


CASONA = House(
    name=config["properties"]["casona"]["name"].get(str),
    price_per_night=config["properties"]["casona"]["price_per_night"].get(int),
    cleaning_fee=config["properties"]["casona"]["cleaning_fee"].get(int),
)
