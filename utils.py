import os
from db import Querier
from email_service import email_serv
from rss import get_posts

if os.environ.get("testing") == "true":
    base_url = "http://127.0.0.1:8080"
else:
    base_url = os.environ["base_url"]


def validate_and_add_feed(q: Querier, rss_url: str):
    feed = get_posts(rss_url)
    if feed is None:
        raise Exception("Could not fetch posts")
    if len(feed.rss_posts) == 0:
        raise Exception("Post history is empty")
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
