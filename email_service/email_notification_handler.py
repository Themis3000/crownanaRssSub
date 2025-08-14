from jinja2 import Environment, FileSystemLoader, select_autoescape
from db.sqlc.models import FeedHistory
from typing import List
from .email_senders.base import EmailSender
import os
from email_service.email_senders.mailgun import Mailgun
from email_service.email_senders.mock import MockEmailSender

service_name = os.environ.get("service_name", "crownanabread")

env = Environment(
    loader=FileSystemLoader("./email_service/templates"),
    autoescape=select_autoescape(default=True)
)
subscribe_template = env.get_template("subscribe_notification.jinja2")
unsubscribe_template = env.get_template("unsubscribe_notification.jinja2")
update_template = env.get_template("update_notification.jinja2")


class EmailNotificationHandler:
    def __init__(self, email_sender: EmailSender):
        self.email_sender = email_sender

    def notify_update(self, to_addr: str, posts: List[FeedHistory], blog_name: str, unsub_link: str, update_link: str):
        email_content = update_template.render(posts=posts, blog_name=blog_name, unsub_link=unsub_link,
                                               update_link=update_link, service_name=service_name)
        self.email_sender.validate_and_send(to_addr=to_addr,
                                            subject=f"New post on {blog_name}!",
                                            content=email_content)

    def notify_subscribe(self, to_addr: str, blog_name: str, confirm_url: str):
        email_content = subscribe_template.render(blog_name=blog_name, confirm_url=confirm_url,
                                                  service_name=service_name)
        self.email_sender.validate_and_send(to_addr=to_addr,
                                            subject=f"Confirm your subscription to {blog_name}",
                                            content=email_content)

    def notify_unsubscribe(self, to_addr: str, blog_name: str):
        email_content = subscribe_template.render(blog_name=blog_name, service_name=service_name)
        self.email_sender.validate_and_send(to_addr=to_addr,
                                            subject=f"{blog_name} unsubscribe confirmation",
                                            content=email_content)


def email_notification_handler_builder() -> EmailNotificationHandler:
    if os.environ.get("testing") == "true":
        return EmailNotificationHandler(email_sender=MockEmailSender())

    from_addr = os.environ.get("from_addr")
    if from_addr is None:
        raise Exception("Environment variable 'from_addr' is not set, and testing mode is not enabled!")
    auth = os.environ.get('mailgun_api')
    if auth is None:
        raise Exception("Environment variable 'mailgun_api' is not set, and testing mode is not enabled!")

    return EmailNotificationHandler(email_sender=Mailgun(api_key=auth, from_addr=from_addr))
