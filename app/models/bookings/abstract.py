from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from config import config

from core.console import console

import models.house as h
import models.client as c


@dataclass(order=True, eq=True)
class Booking(ABC):
    house: h.House
    client: c.Client
    booking_type: str
    sheet_row: int
    check_in: datetime = field(compare=True, repr=True)
    check_out: datetime = field(compare=True, repr=True)
    amount_received: float = field(compare=True, repr=True)
    detail_extra_charged: dict = field(repr=False, default_factory={})

    def __post_init__(self):
        self.convert_string_dates_into_datetime()
        assert self.amount_received > 0, "`amount_received` must be greater than 0"
        assert self.stayed_nights > 0, "stayed_nights must be greater than 0"

        assert self.check_if_total_payed_make_sense()

    @classmethod
    def does_booking_already_exist(
        cls, check_in: datetime, check_out: datetime
    ) -> bool:
        for booking in Booking.bookings:
            if (
                booking.check_in <= check_in <= booking.check_out
                or booking.check_in <= check_out <= booking.check_out
            ):
                console.log(f"Booking period already exists : {booking}")
                return True
        return False

    @property
    def client_email(self):
        return self.client.email

    @property
    def stayed_nights(self):
        return (self.check_out - self.check_in).days

    @property
    def cleaning_fee(self):
        return self.house.cleaning_fee

    @property
    def price_per_night(self):
        return self.house.price_per_night

    @property
    def no_extras_full_booking_price(self):
        return (self.price_per_night * self.stayed_nights) + self.cleaning_fee

    @property
    def full_booking_price(self):
        return self.no_extras_full_booking_price + self.total_extra_charged

    @property
    def tax_iva(self):
        return config["sii"]["IVA"].get(float)

    @property
    def need_factura(self) -> bool:
        invert_op = getattr(self, "need_factura", None)
        if callable(invert_op):
            return self.need_factura
        return False

    @property
    def total_extra_charged(self) -> float:
        total_extra_charged = 0
        for _, value in self.detail_extra_charged.items():
            total_extra_charged += value
        return total_extra_charged

    @property
    def client_name(self) -> str:
        return self.client.name

    @property
    def client_email(self) -> str:
        return self.client.email

    def convert_string_dates_into_datetime(self):
        self.check_in = datetime.strptime(self.check_in, "%d-%m-%Y")
        self.check_out = datetime.strptime(self.check_out, "%d-%m-%Y")

    @abstractmethod
    def check_if_total_payed_make_sense(self) -> bool:
        pass
