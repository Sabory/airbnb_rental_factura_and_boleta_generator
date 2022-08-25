from . import CommandAbstract
from core.google.spreadsheets import Sheets
from pandas import DataFrame


class GetBookings(CommandAbstract):
    @classmethod
    def perform(cls) -> DataFrame:
        sheets_client = Sheets()
        df = sheets_client.get_dataframe_from_worksheet()
        return df
