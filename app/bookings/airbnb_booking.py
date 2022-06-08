from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import pytz
chileanTZ = pytz.timezone('America/Santiago')

from console import console
from bookings.abstract import Booking
import properties as p

@dataclass
class AirbnbBooking(Booking):
    deposit_amount_from_airbnb : float = field(default=0)
    type_name : str = field(init=False, repr=True, default="airbnb_booking")
    need_factura : bool = False
    airbnb_fee: float= field(init=False, repr=False, default=p.AIRBNB_FEE)
    original_price_charge: float = field(init=False, repr=False)
    airbnb_fee_amount: float = field(init=False, repr=False)    
    
    def __post_init__(self):
        assert self.deposit_amount_from_airbnb > 0, "`deposit_amount_from_airbnb` must be greater than 0"
        super().__post_init__()
        self.calculate_airbnb_total_charged()

    def calculate_airbnb_total_charged(self) -> None:
        console.log("Calculating true price charge by us in Airbnb.")
        price_all_nights = self.house.price_per_night * self.stayed_nights
        self.original_price_charge = price_all_nights + self.cleaning_fee
        self.airbnb_fee_amount = (self.original_price_charge * self.airbnb_fee) * (1+self.tax_iva)

        #console.log("Total price charged by us in Airbnb:", "${:,}".format(self.original_price_charge))
        console.log(f"Total payment amount return different values than (Airbnb total fee amount + original price charge on Airnbn:\n"
                            + f" - Total received payment: {self.total_payment_amount}\n"
                            + f" - Airbnb total fee amount charged: {self.airbnb_fee_amount}\n"
                            + f" - Airbnb original price charged: {self.original_price_charge}")

        
        assert abs(self.deposit_amount_from_airbnb - (self.original_price_charge - self.airbnb_fee_amount)) < 100, "Deposit amount from Airbnb is not correct"

        delta = self.total_payment_amount - (self.original_price_charge - self.airbnb_fee_amount)        
        if delta > 0:
            console.log(f"Total payment amount is greater than amount deposited by Airbnb  (delta: {delta})")
            _i = input('Have you charged additional amounts? (y/n)')
            if not _i.lower() in ('y', 'yes'):
                raise ValueError("Total payment amount is greater than amount deposited by Airbnb and no additional amounts has being charged")
        console.log("Total input payment amount is correct", style="bold green")
   
    def generate_factura_for_airbnb_service(self) -> None:
        pass
    
    @classmethod
    def create_instance_from_inputs(cls):
        booking_fields = super().ask_needed_fields()
        booking_fields['deposit_amount_from_airbnb'] = float(input("Deposit amount received from Airbnb: "))
        need_factura = str(input('Does this booking need factura? (y/n):'))
        if need_factura.lower() in  ('y', 'yes'):
            booking_fields['need_factura'] = True
        else:
            booking_fields['need_factura'] = False
        

        return cls(type_name=cls.type_name, **booking_fields)