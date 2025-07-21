from abc import ABC, abstractmethod
from rss import RssUpdates
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader("./email_service/templates"),
    autoescape=select_autoescape()
)
subscribe_template = env.get_template("subscribe_notification.jinja2")
unsubscribe_template = env.get_template("unsubscribe_notification.jinja2")
update_template = env.get_template("update_notification.jinja2")


class BaseEmail(ABC):
    @abstractmethod
    def send_email(self, to_addr: str, subject: str, content: str):
        pass

    def notify_update(self, to_addr: str, blog_update: RssUpdates):
        email_content = update_template.render(blog_update=blog_update)
        self.send_email(to_addr=to_addr,
                        subject=f"New post on {blog_update.blog_name}!",
                        content=email_content)

    def notify_subscribe(self, to_addr: str, blog_name: str, confirm_url: str):
        email_content = subscribe_template.render(blog_name=blog_name, confirm_url=confirm_url)
        self.send_email(to_addr=to_addr,
                        subject=f"Confirm your subscription to {blog_name}",
                        content=email_content)

    def notify_unsubscribe(self, to_addr: str, blog_name: str):
        email_content = subscribe_template.render(blog_name=blog_name)
        self.send_email(to_addr=to_addr,
                        subject=f"{blog_name} unsubscribe confirmation",
                        content=email_content)
