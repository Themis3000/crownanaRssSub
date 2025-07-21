import os
from .base import BaseEmail
from .amazon_ses import SesEmail
from .mock import MockEmail

if os.environ.get("testing") == "true":
    email_serv = MockEmail()
else:
    email_serv = SesEmail()
