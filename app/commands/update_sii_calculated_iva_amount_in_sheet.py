from .abstract import Command
from core.google import Sheets
from config import config


def _get_cols_map(cell_address):
    return config["google"]["sheets"]["boletas"]["cells_map"][cell_address].get(str)


class UpdateSiiCalulatedIvaAmountIntoSheet(Command):
    SHEET_COL = _get_cols_map("sii_calculated_iva_amount")

    @classmethod
    def perform(cls, sheet_row_to_update: int, sii_calculated_iva_amount: int):
        gc = Sheets()
        gc.update_cell(
            cell_address=f"{cls.SHEET_COL}{sheet_row_to_update}",
            value=sii_calculated_iva_amount,
        )
