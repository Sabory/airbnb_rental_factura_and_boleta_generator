from mailers import MailerAbstract
from presenters.generated_boletas_presenter import GeneratedBoletasPresenter


class NotifyClientAboutBookingBoletas(MailerAbstract):
    @classmethod
    def perform(cls, email_to, boletas_paths):
        presenter = GeneratedBoletasPresenter.get(email_to, boletas_paths)
        cls.send(presenter=presenter)
