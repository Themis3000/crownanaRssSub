import os
from db import Querier
from email_service import email_serv
from rss import get_posts

if os.environ.get("testing") == "true":
    base_url = "http://127.0.0.1:8080"
else:
    base_url = os.environ["base_url"]


class EmptyRSS(Exception):
    pass


def validate_and_add_feed(q: Querier, rss_url: str):
    feed = get_posts(rss_url)
    if len(feed.rss_posts) == 0:
        raise EmptyRSS()
    last_post = feed.rss_posts[0]
    query = q.create_feed(rss_url=rss_url,
                          feed_name=feed.blog_name,
                          last_post_id=last_post.post_id,
                          last_post_pub=last_post.get_datetime())
    return query


def add_subscriber(q: Querier, rss_url: str, sub_email: str):
    feed = q.get_feed_by_rss(rss_url=rss_url)
    if feed is None:
        feed = validate_and_add_feed(q=q, rss_url=rss_url)
    subscriber = q.add_subscriber(feed_id=feed.feed_id, email=sub_email)
    confirm_url = f"{base_url}/sub_confirm?sub_id={subscriber.subscriber_id}&code={subscriber.confirmation_code}"
    email_serv.notify_subscribe(to_addr=sub_email, blog_name=feed.feed_name, confirm_url=confirm_url)
    return subscriber


class InvalidConfirmationCode(Exception):
    pass


class InvalidSubscriber(Exception):
    pass


def confirm_subscription(q: Querier, subscriber_id: int, confirmation_code: int):
    subscriber = q.get_subscriber(subscriber_id=subscriber_id)
    if subscriber is None:
        raise InvalidSubscriber()
    if subscriber.confirmation_code != confirmation_code:
        raise InvalidConfirmationCode()
    q.confirm_subscription(subscriber_id=subscriber_id)


def remove_subscription(q: Querier, subscriber_id: int, confirmation_code: int):
    subscriber = q.get_subscriber(subscriber_id=subscriber_id)
    if subscriber is None:
        raise InvalidSubscriber()
    if subscriber.confirmation_code != confirmation_code:
        raise InvalidConfirmationCode()
    blog = q.get_feed(feed_id=subscriber.feed_id)
    q.remove_subscription(subscriber_id=subscriber_id)
    email_serv.notify_unsubscribe(to_addr=subscriber.email, blog_name=blog.feed_name)
