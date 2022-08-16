from app import presenters
from presenters import PresenterAbstract


class GeneratedBoletasPresenter(PresenterAbstract):
    @classmethod
    def get(cls, email_to, boletas_paths) -> dict:
        cls.presenter["email_to"] = email_to
        cls.presenter["subject"] = cls._subject()
        cls.presenter["content"] = cls._content()
        cls.presenter["attachments"] = boletas_paths

        return cls.presenter

    def _subject():
        return "Boletas arriendo Casona San Francisco"

    def _content():
        content = """
            Hola!

            Esperarmos que lo hayan pasado increible en su estadía en la Casona de San Francisco 😊.

            Adjunto se encuentran las boletas de su estadía.

            Saludos!
        """

        return content
