from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import config


class Drive:
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    # fmt: off
    DEFAULT_PARENT_FOLDER_ID = (
        config["google"]["drive"]["default_parent_folder_id"].get()
    )
    # fmt: on

    COLOR_PALETTE = {
        "Chocolate ice cream": "#ac725e",
        "Old brick red": "#d06b64",
        "Cardinal": "#f83a22",
        "Wild straberries": "#fa573c",
        "Mars orange": "#ff7537",
        "Yellow cab": "#ffad46",
        "Spearmint": "#42d692",
        "Vern fern": "#16a765",
        "Asparagus": "#7bd148",
        "Slime green": "#b3dc6c",
        "Desert sand": "#fbe983",
        "Macaroni": "#fad165",
        "Sea foam": "#92e1c0",
        "Pool": "#9fe1e7",
        "Denim": "#9fc6e7",
        "Rainy sky": "#4986e7",
        "Blue velvet": "#9a9cff",
        "Purple dino": "#b99aff",
        "Mouse": "#8f8f8f",
        "Mountain grey": "#cabdbf",
        "Earthworm": "#cca6ac",
        "Bubble gum": "#f691b2",
        "Purple rain": "#cd74e6",
        "Toy eggplant": "#a47ae2",
    }

    def __init__(self):
        self.client = build("drive", "v3", credentials=self.get_credentials())

    @classmethod
    def get_credentials(cls) -> Credentials:
        return Credentials.from_service_account_file(
            config["google"]["credentials_path"].get(), scopes=cls.SCOPES
        )

    def upload_file(
        self,
        file_path: str,
        name: str,
        parent_folder_id: str = None,
        mime_type: str = "application/pdf",
    ) -> str:
        parent_folder_id = self._set_default_parent_folder_if_not_provided(
            parent_folder_id
        )

        file_metadata = {
            "name": name,
            "parents": [parent_folder_id],
        }

        media = MediaFileUpload(file_path, mimetype=mime_type)
        # pylint: disable=maybe-no-member
        file = (
            self.client.files()
            .create(body=file_metadata, media_body=media, fields="webViewLink")
            .execute()
        )

        return file.get("webViewLink")

    def get_folder_id_by_name(self, name: str) -> str:
        results = (
            self.client.files()
            .list(
                q=f"name='{name}' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id)",
            )
            .execute()
        )
        items = results.get("files", [])

        if not items:
            print(f'Folder with name "{name}" not found.')
            return None

        return items[0].get("id")

    def create_folder(self, name: str, parent_folder_id: str = None) -> str:
        parent_folder_id = self._set_default_parent_folder_if_not_provided(
            parent_folder_id
        )

        file_metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_folder_id],
        }

        file = self.client.files().create(body=file_metadata, fields="id").execute()

        return file.get("id")

    def get_or_create_folder(self, name: str, parent_folder_id: str = None) -> str:
        parent_folder_id = self._set_default_parent_folder_if_not_provided(
            parent_folder_id
        )

        folder_id = self.get_folder_id_by_name(name)
        if folder_id:
            return folder_id

        return self.create_folder(name, parent_folder_id)

    def _set_default_parent_folder_if_not_provided(self, parent_folder_id: str):
        return parent_folder_id or self.DEFAULT_PARENT_FOLDER_ID
