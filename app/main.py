from console import console

import pytz
chileanTZ = pytz.timezone('America/Santiago')
from bookings.airbnb_booking import AirbnbBooking
from house import House
from sii import BookingSIIManager

def main():
    casona = House(name="Casona", price_per_night=300000, cleaning_fee=80000)

    booking = {
        "house" : casona,
        "check_in": "01-02-2022", # B
        "check_out": "05-02-2022", # C
        "name": "Constanza Javiera Silva", # E
        "email": "conysilvagg@gmail.com", # F
        "total_payment_amount": 1200000,  # T -> Total amount recieved
        "deposit_amount_from_airbnb": 1200000,
        "need_factura": False
    }
    airbnb = AirbnbBooking(**booking)
    
    BookingSIIManager(airbnb)



if __name__ == '__main__':
    pass

