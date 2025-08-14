from .base import EmailSender
import requests


class MailgunFailure(Exception):
    pass


class Mailgun(EmailSender):
    def __init__(self, from_addr: str, api_key: str):
        super().__init__()
        self.from_addr = from_addr
        self.api_key = api_key
        # TODO Validate api key so an invalid key is caught right at startup!

    def send_email(self, to_addr: str, subject: str, content: str):
        response = requests.post("https://api.mailgun.net/v3/rss.crownanabread.com/messages",
                                 auth=('apt', self.api_key),
                                 files={"from": self.from_addr,
                                        "to": to_addr,
                                        "subject": subject,
                                        "html": content})

        if not response.ok:
            raise MailgunFailure(f"Got non-ok response: {response.text}")
