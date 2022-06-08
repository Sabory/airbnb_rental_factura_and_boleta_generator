from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import pytz
chileanTZ = pytz.timezone('America/Santiago')

from console import console
from bookings.abstract import Booking


@dataclass
class DirectBooking(Booking):
    type_name: str = "direct_booking"
    need_factura : bool = False

    def generate_factura_for_airbnb_service(self):
        console.log("Direct bookings doesnt need facturas because no services was provided.")
        return None
    
