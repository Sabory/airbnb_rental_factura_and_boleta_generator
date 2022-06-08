from dataclasses import dataclass, field
from typing import ClassVar, List

@dataclass(eq=True)
class House:
   name : str
   price_per_night : float
   cleaning_fee : float
   _id : str = field(init=False, repr=False)

   _houses : ClassVar[list] = []

   def __post_init__(self):
      _id = self.name.lower().replace(' ', '_')
      if _id in House.get_houses_ids():
         raise AttributeError(f"House id `{_id}` already exists.")
      self._id = _id
      House._houses.append(self)

   @classmethod
   def get_houses_ids(cls) -> List[str]:
      """ Get a list of all houses ids. """
      #! Warning: this get a list. not a generator... if many will be slow.
      return [house._id for house in House._houses]

   def change_price_per_night(self, new_price_per_night: float) -> None:
      """ Change the price per night of the house. """
      self.price_per_night = new_price_per_night
   
   def change_cleaning_fee(self, new_cleaning_fee: float) -> None:
      """ Change the cleaning fee of the house. """
      self.cleaning_fee = new_cleaning_fee
