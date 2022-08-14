from pandas import DataFrame

from config import config

from core.messenger.slack import Slack
from commands.get_pending_documents import GetPendingDocuments
from commands.get_latest_booking import GetLatestBooking


class RemindPendingDocuments:
    @classmethod
    def perform(cls) -> DataFrame:
        pending_documents = GetPendingDocuments.perform()
        cls._inform_pending_documents(pending_documents)

    def _inform_pending_documents(pending_documents) -> DataFrame:
        def get_oldest_document(pending_documents):
            return pending_documents.iloc[0]

        def get_name_from_pending_doc(pending_doc):
            return pending_doc["Nombre cliente"]

        def get_date_from_pending_doc(pending_doc):
            return pending_doc["Fecha entrada"]

        pendings_amount = len(pending_documents)
        if pendings_amount > 0:
            oldest_one = get_oldest_document(pending_documents)
            msg = (
                f" :alert: *PENDIENTES*: Hay {pendings_amount} {'documentos pendientes' if pendings_amount > 1 else 'documento pendiente'} por generar \n"
                f"> Pendiente más viejo: {get_name_from_pending_doc(oldest_one)} - {get_date_from_pending_doc(oldest_one)}"
            )

            Slack.send_message(
                message=msg, channel=config["slack"]["channels"]["casona"].get()
            )
            return

        latest_booking = GetLatestBooking.perform()
        Slack.send_message(
            ":white_check_mark: *PENDIENTES*: No hay documentos pendientes de generar."
            f"\n> Última reserva registrada: {latest_booking['Nombre cliente']} - {latest_booking['Fecha entrada']}"
        )
        return
