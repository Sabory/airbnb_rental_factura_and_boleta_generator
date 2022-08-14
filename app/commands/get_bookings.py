from .abstract import Command
from core.google.spreadsheets import Sheets


class GetBookings(Command):
    @classmethod
    def perform(cls):
        sheets_client = Sheets()
        df = sheets_client.get_dataframe_from_worksheet()
        return df
