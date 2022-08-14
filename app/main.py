from core.console import console

from models.bookings.controller import Controller
from models.servicio_impuesto_interno.bookings_dte_wraper import BookingSIIManager

from presenters.pending_documents_presenter import PendingDocumentsPresenter

from commands.update_documents_into_sheet import UpdateDocumentIntoDocumentsSheet
from commands.update_sii_calculated_iva_amount_in_sheet import (
    UpdateSiiCalulatedIvaAmountIntoSheet,
)
from commands.upload_document_into_drive import UploadDocumentIntoDrive

import click


@click.command()
def main():
    pending_bookings = PendingDocumentsPresenter.get()
    for booking in pending_bookings:
        print(booking)

        files_status = booking.pop("files_statuses")

        booking = Controller.create_booking(**booking)
        booking_sii_manager = BookingSIIManager(booking)

        update_sii_calculated_iva_amount(
            booking.sheet_row, booking_sii_manager.iva_calculated_by_sii
        )

        if need_to_generate_boleta_with_taxes(files_status):
            console.log("Generando boleta afecta")
            generate_boleta(booking_sii_manager, "boleta_afecta")

        if need_to_generate_boleta_without_taxes(files_status):
            console.log("Generando boleta exenta")
            generate_boleta(booking_sii_manager, "boleta_exenta")

        # TODO: Send email

        # TODO: Check that this works
        if booking.need_factura:
            console.log("Generando factura")
            booking_sii_manager.generate_factura()


def generate_boleta(sii_manager: BookingSIIManager, boleta_type: str):
    boleta_generators = {
        "boleta_afecta": sii_manager.generate_boleta_with_taxes,
        "boleta_exenta": sii_manager.generate_boleta_without_taxes,
    }

    boleta_generator = boleta_generators[boleta_type]
    boleta = boleta_generator()

    update_documents_into_sheet(sii_manager.booking.sheet_row, boleta_type, boleta.id)

    webview_URL = upload_documents_into_drive(sii_manager.booking, boleta)

    update_docuemnt_webview_into_sheet(
        sii_manager.booking.sheet_row, boleta_type, webview_URL
    )


def upload_documents_into_drive(booking, document) -> str:
    file_webview_URL = UploadDocumentIntoDrive.perform(
        client_name=booking.client.name,
        check_in_date=booking.check_in_date.date(),
        file_path=document.path,
        file_name=document.path.split("/")[-1],
    )
    return file_webview_URL


def update_sii_calculated_iva_amount(sheet_row, calculated_amount):
    UpdateSiiCalulatedIvaAmountIntoSheet.perform(sheet_row, calculated_amount)


def need_to_generate_boleta_with_taxes(files_statuses):
    return files_statuses["boleta_afecta"] == 0


def need_to_generate_boleta_without_taxes(files_statuses):
    return files_statuses["boleta_exenta"] == 0


def update_documents_into_sheet(
    sheet_row_tu_update: int, document_type: str, document_id: str
):
    keys_to_update = {
        document_type: document_id,
    }
    UpdateDocumentIntoDocumentsSheet.perform(sheet_row_tu_update, **keys_to_update)


def update_docuemnt_webview_into_sheet(
    sheet_row_tu_update: int, document_type: str, document_webview_URL: str
):
    keys_to_update = {
        f"{document_type}_url": document_webview_URL,
    }
    UpdateDocumentIntoDocumentsSheet.perform(sheet_row_tu_update, **keys_to_update)


if __name__ == "__main__":
    main()
