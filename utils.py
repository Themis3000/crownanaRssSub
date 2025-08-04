import os
from datetime import timedelta
from db import AsyncQuerier
from db.sqlc.models import Feed
from email_service import email_serv
from rss import get_posts, RssUpdates
from db.sqlc.queries import add_feed_historyParams

if os.environ.get("testing") == "true":
    base_url = "http://127.0.0.1:8080"
else:
    base_url = os.environ["base_url"]


class EmptyRSS(Exception):
    pass


async def store_posts(q: AsyncQuerier, updates: RssUpdates, feed_id: int):
    for post in updates.rss_posts:
        if q.post_id_exists(feed_id=feed_id, unique_id=post.post_id):
            # Duplicate post id already exists. What should I do in such a case?
            # This could be caused by a duplicate guid or title (if no guid is present)
            continue
        await q.add_feed_history(add_feed_historyParams(
            feed_id=feed_id,
            post_date=post.get_datetime(),
            title=post.title,
            unique_id=post.post_id,
            link=post.link
        ))


async def validate_and_add_feed(q: AsyncQuerier, rss_url: str) -> Feed:
    posts = get_posts(rss_url)

    if len(posts.rss_posts) == 0:
        raise EmptyRSS()

    feed = await q.create_feed(rss_url=rss_url, feed_name=posts.blog_name)
    await store_posts(q=q, updates=posts, feed_id=feed.feed_id)
    return feed


async def add_subscriber(q: AsyncQuerier, rss_url: str, sub_email: str, notification_delta=timedelta(days=1)):
    feed = await q.get_feed_by_rss(rss_url=rss_url)
    if feed is None:
        feed = validate_and_add_feed(q=q, rss_url=rss_url)
    subscriber = await q.add_subscriber(feed_id=feed.feed_id, email=sub_email, notification_interval=notification_delta)
    confirm_url = f"{base_url}/sub_confirm?sub_id={subscriber.subscriber_id}&code={subscriber.confirmation_code}"
    email_serv.notify_subscribe(to_addr=sub_email, blog_name=feed.feed_name, confirm_url=confirm_url)
    return subscriber, feed


class InvalidConfirmationCode(Exception):
    pass


class InvalidSubscriber(Exception):
    pass


async def confirm_subscription(q: AsyncQuerier, subscriber_id: int, confirmation_code: int):
    subscriber = await q.get_subscriber(subscriber_id=subscriber_id)
    if subscriber is None:
        raise InvalidSubscriber()
    if subscriber.confirmation_code != confirmation_code:
        raise InvalidConfirmationCode()
    await q.confirm_subscription(subscriber_id=subscriber_id)


async def remove_subscription(q: AsyncQuerier, subscriber_id: int, confirmation_code: int):
    subscriber = await q.get_subscriber(subscriber_id=subscriber_id)
    if subscriber is None:
        raise InvalidSubscriber()
    if subscriber.confirmation_code != confirmation_code:
        raise InvalidConfirmationCode()
    blog = await q.get_feed(feed_id=subscriber.feed_id)
    await q.remove_subscription(subscriber_id=subscriber_id)
    email_serv.notify_unsubscribe(to_addr=subscriber.email, blog_name=blog.feed_name)
