# SII manager for property bookings
This code if for the purpose of managing the SII needed documents (factura & boleta) when rentaling a property.
For now, a property rental can be done through Airbnb or Direct booking.
Everytime a property is rented, a new `boleta` for the rental is needed.

If:
   - When booking was through Airbnb: also is needed a `factura compra` for the service provided by Airbnb.
   - When direct booking needs a factura, then a `factura venta` is needed instead of a `boleta`. 
   - This flow does not support Airbnb with factura. 

**Database classes not created yet**

## Instalation


## Usage
- First create `Booking` and `BookingSIIManager`:
```python
    booking = {
        "house" : House(name="Casona", price_per_night=300000, cleaning_fee=80000),
        "check_in": "29-03-2022",
        "check_out": "01-04-2022",
        "client": Client(name="Bastean Faundez", email="icorream213@gmail.com"),
        "amount_received": 655724,
        "detail_extra_charged": {
            "pool": 0,
            "others": 0,
        },
        "booking_type": "airbnb_booking",
    }


    booking = Controller.create_booking(**booking)

    BookingSIIManager(booking)
```

- Then, you can generate the SII documents:
```python
      BookingSIIManager.generate_boleta_with_taxes()
      BookingSIIManager.generate_boleta_without_taxes()
```



