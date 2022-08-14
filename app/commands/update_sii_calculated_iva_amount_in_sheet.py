from .abstract import Command
from core.google import Sheets


class UpdateSiiCalulatedIvaAmountIntoSheet(Command):
    SHEET_COL = "AB"

    @classmethod
    def perform(cls, sheet_row_to_update: int, sii_calculated_iva_amount: int):
        gc = Sheets()
        gc.update_cell(
            cell_address=f"{cls.SHEET_COL}{sheet_row_to_update}",
            value=sii_calculated_iva_amount
        )
