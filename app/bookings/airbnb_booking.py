from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import pytz
chileanTZ = pytz.timezone('America/Santiago')

from console import console
from bookings.abstract import Booking

@dataclass
class AirbnbBooking(Booking):
    type_name = "airbnb_booking"
    need_factura = True
    airbnb_fee: float= field(init=False, repr=False, default=0.03)
    original_price_charge: int = field(init=False, repr=False)
    airbnb_fee_amount: int = field(init=False, repr=False)    
    
    def __post_init__(self):
        super().__post_init__()
        self.calculate_airbnb_total_charged()

    def calculate_airbnb_total_charged(self) -> None:
        console.log("Calculating true price charge by us in Airbnb.")
        price_all_nights = self.price_per_night * self.stayed_nights
        self.original_price_charge = round(price_all_nights + self.cleaning_fee)
        self.airbnb_fee_amount = round((self.original_price_charge * self.airbnb_fee) * (1+self.tax_iva))
        console.log("Total price charged by us in Airbnb:", "${:,.2f}".format(self.original_price_charge))
        if abs(self.total_payment_amount - (self.original_price_charge - self.airbnb_fee_amount)) > 10:
            raise ValueError(f"Total payment amount return different values than (Airbnb total fee amount + original price charge on Airnbn:\n"
                            + f" - Total received payment: {self.total_payment_amount}\n"
                            + f" - Airbnb total fee amount charged: {self.airbnb_fee_amount}\n"
                            + f" - Airbnb original price charged: {self.original_price_charge}")

    def generate_factura_for_airbnb_service(self) -> None:
        pass
    