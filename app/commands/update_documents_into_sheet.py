from .abstract import Command
from core.google import Sheets


class UpdateDocumentIntoDocumentsSheet(Command):
    COL_MAP = {
        "boleta_exenta": "T",
        "boleta_exenta_url": "U",
        "boleta_afecta": "X",
        "boleta_afecta_url": "Y",
    }

    @classmethod
    def perform(cls, sheet_row_to_update: int, **keys_to_update):
        gc = Sheets()
        for key, val in keys_to_update.items():
            try:
                doc_cols = cls.COL_MAP[key]
            except KeyError:
                print(f"{key} is not a valid key")
                continue

            gc.update_cell(cell_address=f"{doc_cols}{sheet_row_to_update}", value=val)
