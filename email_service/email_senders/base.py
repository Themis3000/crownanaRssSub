import textwrap
from abc import abstractmethod, ABC
from email_validator import validate_email, caching_resolver

resolver = caching_resolver(timeout=60)


class EmailSender(ABC):
    @abstractmethod
    def send_email(self, to_addr: str, subject: str, content: str):
        pass

    def validate_and_send(self, to_addr: str, subject: str, content: str):
        email_info = validate_email(to_addr, dns_resolver=resolver)
        sanitized_subject = textwrap.shorten(subject, width=80, placeholder="...")
        self.send_email(to_addr=email_info.normalized, subject=sanitized_subject, content=content)
