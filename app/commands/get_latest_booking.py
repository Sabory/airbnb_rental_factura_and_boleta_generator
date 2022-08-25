from . import CommandAbstract
from commands.get_bookings import GetBookings
from pandas import Series


class GetLatestBooking(CommandAbstract):
    @classmethod
    def perform(cls) -> Series:
        df = GetBookings.perform()
        return cls._get_latest_booking(df)

    def _get_latest_booking(df) -> Series:
        efective_bookings = df.loc[
            (df["Reserva efectiva"] == 1) & (df["Nombre cliente"] != "")
        ]
        return efective_bookings.iloc[-1]
