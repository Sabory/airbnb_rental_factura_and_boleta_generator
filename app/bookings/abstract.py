from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
import pytz
chileanTZ = pytz.timezone('America/Santiago')
from typing import ClassVar
from rich.markdown import Markdown
from console import console
import properties as p
import house as h


@dataclass(order=True, eq=True)
class Booking(ABC):
    house : h.House 
    type_name: str
    check_in: datetime = field(compare=True, repr=True)
    check_out: datetime = field(compare=True, repr=True)
    name: str
    email: str = field(repr=False)
    total_payment_amount: int = field(repr=False)
    need_factura: bool = field(repr=False)
    # Calculated
    stayed_nights: int = field(init=False, repr=True)
    
    # PROPERTIES -> are flield instead of constant because they can be changed (e.x: multiple renting houses)
    price_per_night: ClassVar[float] = p.PRICE_PER_NIGHT
    cleaning_fee: ClassVar[float] = p.CLEANING_FEE
    tax_iva: ClassVar[float] = p.IVA

    bookings : ClassVar[list] = []


    def __post_init__(self):
        self.convert_string_dates_into_datetime()
        self.stayed_nights = self.calculate_stayed_nights()
        assert self.stayed_nights > 0, "stayed_nights must be greater than 0"
        # Check if the booking already exists
        #if Booking.does_booking_already_exist():
        #    raise ValueError("Booking already exists")
        # Add the booking to the list of bookings
        Booking.bookings.append(self)
        

    @classmethod
    def does_booking_already_exist(cls, check_in:datetime, check_out:datetime) -> bool:
        for booking in Booking.bookings:
            if booking.check_in <= check_in <= booking.check_out \
                    or booking.check_in <= check_out <= booking.check_out:
                console.log(f"Booking period already exists : {booking}")
                return True
        return False


    def calculate_stayed_nights(self):
        # check if check_in is string instance
        if isinstance(self.check_in, str):
            raise TypeError("check_in is not a datetime instance")
        if isinstance(self.check_out, str):
            raise TypeError("check_out is not a datetime instance")
        return (self.check_out - self.check_in).days

    def convert_string_dates_into_datetime(self):
        self.check_in = datetime.strptime(self.check_in, '%d-%m-%Y')
        self.check_out = datetime.strptime(self.check_out, '%d-%m-%Y')

    @classmethod
    def ask_needed_fields(cls):
        #! THIS DOES NOT WORK IF IT COMES FROM OTHER THAN BOOKING CLASS.
        console.log(Markdown("# ASKING FOR INPUTS"))
        check_in = str(input('Check in ("23-11-2021"):'))
        check_out = str(input('Check out ("25-11-2021"):'))
        name = str(input('Name:'))
        email = str(input('Email:'))
        total = int(input('Total payment amount'))

        return {
            'check_in': check_in,
            'check_out': check_out,
            'name': name,
            'email': email,
            'total_payment_amount': total
        }


    def does_need_factura(self):
        return self.need_factura

    # TODO: 1. Sacar que montos afectos y no afectos a IVA [x]
    # TODO: 2. Generar boletas afectas y no afectas a IVA y descargarlas!
    # TODO: 3. Generar facturas de compra a Airbnb si es que es elegible o no --> y descargar
