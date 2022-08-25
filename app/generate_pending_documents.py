from core.console import console

from models.bookings.controller import Controller
from models.servicio_impuesto_interno.bookings_dte_wraper import BookingSIIManager

from presenters.pending_documents_presenter import PendingDocumentsPresenter
from mailers.notify_client_about_booking_boletas import NotifyClientAboutBookingBoletas

from commands.update_documents_into_sheet import UpdateDocumentIntoDocumentsSheet
from commands.update_sii_calculated_iva_amount_in_sheet import (
    UpdateSiiCalulatedIvaAmountIntoSheet,
)
from commands.upload_document_into_drive import UploadDocumentIntoDrive


def main():
    pending_bookings = PendingDocumentsPresenter.get()
    for booking_dict in pending_bookings:
        console.log(booking_dict)

        files_status = booking_dict.pop("files_status")

        booking = Controller.create_booking(**booking_dict)
        booking_sii_manager = BookingSIIManager(booking)

        update_sii_calculated_iva_amount(
            booking.sheet_row, booking_sii_manager.iva_calculated_by_sii
        )

        if need_to_generate_document_with_taxes(files_status):
            console.log("Generando boleta afecta")
            generate_document(booking_sii_manager, "boleta_afecta")

        if need_to_generate_document_without_taxes(files_status):
            console.log("Generando boleta exenta")
            generate_document(booking_sii_manager, "boleta_exenta")

        # TODO: WIP -> Send email
        if should_notify_user(booking_sii_manager):
            console.log("Sending email")
            send_boletas_to_client_mail(
                email_to=booking.client.mail,
                files_paths=booking_sii_manager.selling_documents_paths,
            )

        # TODO: WIP -> Generate factura
        if booking.need_factura & need_to_generate_factura(files_status):
            console.log("Generando factura")
            generate_document(booking_sii_manager, "factura")


def generate_document(sii_manager: BookingSIIManager, boleta_type: str):
    BOLETA_GENERATORS = {
        "boleta_afecta": sii_manager.generate_document_with_taxes,
        "boleta_exenta": sii_manager.generate_document_without_taxes,
        "factura": sii_manager.generate_factura,
    }

    boleta_generator = BOLETA_GENERATORS[boleta_type]
    document = boleta_generator()

    update_documents_into_sheet(sii_manager.booking.sheet_row, boleta_type, document.id)

    webview_URL = upload_documents_into_drive(sii_manager.booking, document)

    update_document_webview_into_sheet(
        sii_manager.booking.sheet_row, boleta_type, webview_URL
    )


def upload_documents_into_drive(booking, document) -> str:
    file_webview_URL = UploadDocumentIntoDrive.perform(
        client_name=booking.client.name,
        check_in_date=booking.check_in.date(),
        file_path=document.path,
        file_name=document.path.split("/")[-1],
    )
    return file_webview_URL


def update_sii_calculated_iva_amount(sheet_row, calculated_amount):
    UpdateSiiCalulatedIvaAmountIntoSheet.perform(sheet_row, calculated_amount)


def need_to_generate_document_with_taxes(files_statuses):
    return files_statuses["boleta_afecta"] == 0


def need_to_generate_document_without_taxes(files_statuses):
    return files_statuses["boleta_exenta"] == 0


def need_to_generate_factura(files_statuses):
    return files_statuses["factura"] in [0, "0"]


def update_documents_into_sheet(
    sheet_row_tu_update: int, document_type: str, document_id: str
):
    keys_to_update = {
        document_type: document_id,
    }
    UpdateDocumentIntoDocumentsSheet.perform(sheet_row_tu_update, **keys_to_update)


def update_document_webview_into_sheet(
    sheet_row_tu_update: int, document_type: str, document_webview_URL: str
):
    keys_to_update = {
        f"{document_type}_url": document_webview_URL,
    }
    UpdateDocumentIntoDocumentsSheet.perform(sheet_row_tu_update, **keys_to_update)


def should_notify_user(booking_sii_manager):
    return (
        booking_sii_manager.has_selling_documents
        & booking_sii_manager.booking.client.has_email
    )


def send_boletas_to_client_mail(email_to: str, files_paths: list) -> None:
    NotifyClientAboutBookingBoletas.perform(
        email_to="icorream213@gmail.com", boletas_paths=files_paths
    )


if __name__ == "__main__":
    main()
