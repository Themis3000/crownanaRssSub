from .base import BaseEmail


class SesEmail(BaseEmail):
    def send_email(self, to_addr: str, subject: str, content: str):
        raise NotImplemented()
