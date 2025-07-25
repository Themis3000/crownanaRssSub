import os
from .base import BaseEmail
from .mailgun import Mailgun
from .mock import MockEmail

if os.environ.get("testing") == "true":
    email_serv = MockEmail()
else:
    email_serv = Mailgun()
