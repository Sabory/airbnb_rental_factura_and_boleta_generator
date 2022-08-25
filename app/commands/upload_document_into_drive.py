from datetime import datetime, date
import locale

locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
from . import CommandAbstract
from core.google import Drive
from models.servicio_impuesto_interno.sii_dte.abstract import Document


class UploadDocumentIntoDrive(CommandAbstract):
    @classmethod
    def perform(
        cls, client_name: str, check_in_date: date, file_path: str, file_name: str
    ):
        drive_client = Drive()

        booking_folder_id = cls._get_or_create_document_folder(
            drive_client, client_name, check_in_date
        )

        webview_URL = drive_client.upload_file(
            file_path=file_path,
            name=file_name,
            parent_folder_id=booking_folder_id,
        )
        return webview_URL

    @classmethod
    def _get_or_create_document_folder(
        cls, drive: Drive, client_name: str, check_in_date: date
    ) -> str:
        year_folder_id = cls._get_year_folder(drive, check_in_date)

        month_folder_id = cls._get_month_folder(drive, check_in_date, year_folder_id)

        booking_folder_id = cls._get_booking_folder(
            drive,
            client_name,
            check_in_date,
            month_folder_id,
        )
        return booking_folder_id

    def _get_check_in_date_from_document(document) -> date:
        return datetime.strftime(document.file_name.split("_")[1], "%d-%m-%Y").date()

    def _get_client_name_from_document(document) -> str:
        return document.file_name.split("_")[0].replace("-", " ")

    def _get_year_folder(drive: Drive, check_in_date: date) -> str:
        return drive.get_or_create_folder(name=str(check_in_date.year))

    def _get_month_folder(
        drive: Drive, check_in_date: date, year_folder_id: str
    ) -> str:
        month_folder_name = check_in_date.strftime("%m/%Y (%B)")

        folder_id = drive.get_or_create_folder(
            name=month_folder_name, parent_folder_id=year_folder_id
        )
        return folder_id

    def _get_booking_folder(
        drive: Drive, client_name: str, check_in_date: date, month_folder_id: str
    ) -> str:
        folder_name_date_part = check_in_date.strftime("%d/%m (%b)")
        folder_name = f"{folder_name_date_part}, {client_name}"

        folder_id = drive.get_or_create_folder(
            name=folder_name, parent_folder_id=month_folder_id
        )
        return folder_id
