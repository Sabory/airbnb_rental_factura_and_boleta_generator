from . import CommandAbstract
from core.google import Sheets
from config import config


def _get_config_col(cell_address):
    return config["google"]["sheets"]["boletas"]["cells_map"][cell_address].get(str)


class UpdateDocumentIntoDocumentsSheet(CommandAbstract):

    COL_MAP = {
        "boleta_exenta": _get_config_col("boleta_exenta"),
        "boleta_exenta_url": _get_config_col("boleta_exenta_url"),
        "boleta_afecta": _get_config_col("boleta_afecta"),
        "boleta_afecta_url": _get_config_col("boleta_afecta_url"),
        "factura": _get_config_col("factura"),
        "factura_url": _get_config_col("factura_url"),
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
