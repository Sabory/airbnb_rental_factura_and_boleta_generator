from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
import pytz
chileanTZ = pytz.timezone('America/Santiago')
from rich.markdown import Markdown
from console import console



@dataclass
class Booking(ABC):
    type_name: str
    need_factura: bool
    check_in: str
    check_out: str
    name: str
    email: str
    total_payment_amount: int 
    # Calculated
    stayed_nights: int = field(init=False, repr=True)
    # PROPERTIES
    price_per_night: int= field(repr=False, default=300000)
    cleaning_fee: int= field(repr=False, default=60000)
    tax_iva: float= field(repr=False, default=p.IVA)

    def __post_init__(self):
        self.convert_string_dates_into_datetime()
        self.stayed_nights = self.calculate_stayed_nights()
        assert self.stayed_nights > 0, "stayed_nights must be greater than 0"

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
    def create_instance_from_inputs(cls):
        console.log(Markdown("# ASKING FOR INPUTS"))
        check_in = str(input('Check in ("23-11-2021"):'))
        check_out = str(input('Check out ("25-11-2021"):'))
        name = str(input('Name:'))
        email = str(input('Email:'))
        total = int(input('Total payment amount'))
        return cls(check_in=check_in, check_out=check_out, name=name, email=email, total_payment_amount=total)

    def does_need_factura(self):
        return self.need_factura

    # TODO: 1. Sacar que montos afectos y no afectos a IVA [x]
    # TODO: 2. Generar boletas afectas y no afectas a IVA y descargarlas!
    # TODO: 3. Generar facturas de compra a Airbnb si es que es elegible o no --> y descargar
