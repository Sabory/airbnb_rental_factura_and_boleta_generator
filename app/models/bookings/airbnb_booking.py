from dataclasses import dataclass, field
from typing import ClassVar

from config import config

from core.console import console
from .abstract import Booking


@dataclass
class AirbnbBooking(Booking):
    booking_type: str = field(init=False, repr=True, default="airbnb_booking")
    need_factura: bool = True

    AIRBNB_FEE: ClassVar[float] = config["airbnb"]["service_fee"].get(float)

    def __post_init__(self):
        super().__post_init__()

    def check_if_total_payed_make_sense(self) -> bool:
        if abs(self.amount_received - self.payment_theoric_value) > 100:
            console.log("`amount_received` must be close to `payment_theoric_value`")
            console.log({self.amount_received, self.payment_theoric_value})

            res = input("Want to continue anyway? (y/n) ")
            if res != "y":
                return False
        return True

    def generate_factura_for_airbnb_service(self) -> None:
        pass

    @property
    def facturable_amount(self) -> int:
        return int(self.airbnb_fee_amount)

    @property
    def airbnb_fee_amount(self) -> float:
        return (self.no_extras_full_booking_price * self.AIRBNB_FEE) * (
            1 + self.tax_iva
        )

    @property
    def payment_theoric_value(self) -> int:
        return int(
            round(
                (self.no_extras_full_booking_price - self.airbnb_fee_amount)
                + self.total_extra_charged,
                0,
            )
        )
