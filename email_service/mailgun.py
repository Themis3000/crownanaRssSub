from .base import BaseEmail
import requests
import os

from_addr = os.environ.get("from_addr")
auth = os.environ.get('mailgun_api')


class MailgunFailure(Exception):
    pass


class Mailgun(BaseEmail):
    def send_email(self, to_addr: str, subject: str, content: str):
        response = requests.post("https://api.mailgun.net/v3/rss.crownanabread.com/messages",
                                 auth=('apt', auth),
                                 files={"from": from_addr,
                                        "to": to_addr,
                                        "subject": subject,
                                        "html": content})

        if not response.ok:
            raise MailgunFailure(f"Got non-ok response: {response.text}")
