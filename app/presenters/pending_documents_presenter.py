from presenters import PresenterAbstract
from commands.get_pending_documents import GetPendingDocuments
from models.client import Client
from models.house import CASONA

import pandas as pd


class PendingDocumentsPresenter(PresenterAbstract):
    @classmethod
    def get(cls) -> list:
        pendings = cls.__bookings()

        pendings_bookings = []
        for i, row in pendings.iterrows():
            pendings_bookings.append(cls.__parse_booking(row))
        return pendings_bookings

    @staticmethod
    def __bookings() -> pd.DataFrame:
        return GetPendingDocuments.perform()

    @classmethod
    def __parse_booking(cls, raw_booking):
        return {
            "sheet_row": int(raw_booking["sheet_row"]),
            "house": CASONA,
            "booking_type": raw_booking["booking_type"],
            "check_in": raw_booking["check_in"],
            "check_out": raw_booking["check_out"],
            "client": Client(raw_booking["client_name"], raw_booking["client_email"]),
            "amount_received": int(raw_booking["amount_received"]),
            "detail_extra_charged": {
                "pool": int(raw_booking["extra_pool"]),
                "others": int(raw_booking["extra_others"]),
            },
            "files_status": {
                "boleta_exenta": int(raw_booking["boleta_exenta_generated"]),
                "boleta_afecta": int(raw_booking["boleta_afecta_generated"]),
                "factura": raw_booking["factura_generated"],
            },
        }
