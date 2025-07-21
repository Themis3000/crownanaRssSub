from .base import BaseEmail
from dataclasses import dataclass
from typing import List


@dataclass
class LoggedEmail:
    to: str
    subject: str
    content: str


class MockEmail(BaseEmail):
    def __init__(self):
        self.email_log: List[LoggedEmail] = []
        self.logged_calls = []

    def send_email(self, to_addr: str, subject: str, content: str):
        self.email_log.append(LoggedEmail(to=to_addr, subject=subject, content=content))
        email_message = f"""
        Sent email
        TO: {to_addr}
        SUBJECT: {subject}
        
        {content}
        """
        print(email_message)

    def notify_subscribe(self, **kwargs):
        self.logged_calls.append(kwargs)
        super().notify_subscribe(**kwargs)

    def notify_update(self, to_addr: str, **kwargs):
        self.logged_calls.append(kwargs)
        super().notify_update(**kwargs)

    def notify_unsubscribe(self, **kwargs):
        self.logged_calls.append(kwargs)
        super().notify_unsubscribe(**kwargs)

    def clear_logs(self):
        self.email_log = []
        self.logged_calls = []
