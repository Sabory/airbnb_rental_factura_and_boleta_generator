from .abstract import Command
from commands.get_bookings import GetBookings
import pandas as pd


class GetPendingDocuments(Command):
    COLS = [
        "sheet_row",
        "booking_type",
        "check_in",
        "check_out",
        "client_name",
        "client_email",
        "amount_received",
        "extra_pool",
        "extra_others",
        "boleta_exenta_generated",
        "boleta_afecta_generated",
        "factura_generated",
    ]

    SHEET_SPREAD_FROM_INDEX = 2

    @classmethod
    def perform(cls) -> pd.DataFrame:
        df = cls._get_documents_dataframe()
        df = cls._generate_sheet_row(df, cls.SHEET_SPREAD_FROM_INDEX)
        return cls._get_pending_documents(df)[cls.COLS]

    def _get_documents_dataframe():
        return GetBookings.perform()

    def _get_pending_documents(df):
        return df.loc[
            (
                (df["Boletas boleta_afecta_generated"] != 1)
                | (df["Boletas boleta_excenta_generated"] != 1)
                | (df["factura_generated"] != 1)
            )
            & (df["Reserva efectiva"] == 1)
            & (df["Nombre cliente"] != "")
        ]

    def _generate_sheet_row(df, sheet_row_spread):
        df.reset_index(inplace=True)
        df.rename(columns={"index": "sheet_row"}, inplace=True)
        df.loc[:, "sheet_row"] = df.loc[:, "sheet_row"] + sheet_row_spread
        return df
