import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

from config import config


class Sheets:
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
    ]

    DEFAULT_SHEET_ID = config["google"]["sheets"]["boletas"]["id"].get(str)
    # fmt: off
    DEFAULT_WORKSHEET_NAME = (
        config["google"]["sheets"]["boletas"]["main_worksheet"].get(str)
    )
    # fmt: on

    def __init__(self):
        self.client = gspread.authorize(self.get_credentials())
        self.default_gc = self.get_sheet_by_id()
        self.default_worksheet = self.get_default_worksheet()

    @classmethod
    def get_credentials(cls):
        return Credentials.from_service_account_file(
            config["google"]["credentials_path"].get(str), scopes=cls.SCOPES
        )

    def find_row_matching_string(self, find_by: str, worksheet=None):
        ws = worksheet or self.default_worksheet
        return ws.findall(find_by)

    def get_sheet_by_id(self, sheet_id=None):
        sheet_id = sheet_id or self.DEFAULT_SHEET_ID

        gc = self.client.open_by_key(sheet_id)
        return gc

    def get_dataframe_from_worksheet(self, worksheet=None):
        worksheet = worksheet or self.default_worksheet
        return pd.DataFrame(worksheet.get_all_records())

    def update_cell(self, cell_address, value, ws=None):
        ws = ws or self.default_worksheet
        return ws.update(cell_address, value)

    def get_default_worksheet(self):
        return self.default_gc.worksheet(self.DEFAULT_WORKSHEET_NAME)
