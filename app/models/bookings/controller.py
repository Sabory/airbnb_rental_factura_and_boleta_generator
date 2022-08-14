from . import airbnb_booking, direct_booking
from core.console import console


class Controller:
    BOOKING_TYPES = {
        "airbnb_booking": airbnb_booking.AirbnbBooking,
        "direct_booking": direct_booking.DirectBooking,
    }

    @classmethod
    def create_booking(cls, booking_type: str, **booking_params):
        booking_handler = cls._define_handler_for_booking(booking_type)

        booking = booking_handler(**booking_params)

        return booking

    @classmethod
    def _define_handler_for_booking(cls, selected_booking_type: str):
        for booking_type, handler in cls.BOOKING_TYPES.items():
            if booking_type == selected_booking_type:
                return handler
        console.log(f"Booking type {selected_booking_type} not found")
        return None
