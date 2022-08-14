from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from core.console import console
from .abstract import Booking


@dataclass
class DirectBooking(Booking):
    booking_type: str = field(init=False, repr=True, default="direct_booking")

    def check_if_total_payed_make_sense(self) -> None:
        if abs(self.amount_received - self.payment_theoric_value) > 100:
            console.log("`amount_received` must be close to `payment_theoric_value`")
            console.log({self.amount_received, self.payment_theoric_value})
            res = input("Want to continue anyway? (y/n) ")
            if res != "y":
                return False
        return True

    @property
    def payment_theoric_value(self) -> int:
        return int(
            round(
                self.no_extras_full_booking_price + self.total_extra_charged,
                0,
            )
        )