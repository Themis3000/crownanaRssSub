from db import QueryManager
from db.sqlc.models import Feed
from rss import get_posts, RssUpdates
from cachetools import TTLCache, cached
from email_service import email_serv
from typing import Tuple
import time


# This isn't friendly to multiple concurrent workers
# Things probably won't break technically speaking, but it will cause duplicate fetches to the rss endpoint
# We don't want to get rate limited or get inconsistent responses...
# We probably want to add the db as a cache layer for this if we scale to multiple workers.
post_caching = cached(cache=(TTLCache(maxsize=10, ttl=600)))
caching_get_posts = post_caching(get_posts)


# Handles doing work and the priority of what work to do. Will run forever.
def do_work():
    while True:
        feed, rss_updates = do_feed_job()

        if feed is None:
            feed, rss_updates = do_feed_job()

        if feed is None:
            # There is no job to do. Wait 30 seconds before checking again...
            time.sleep(30)
            continue

        # Do up to 200 mail jobs at a time. If there's more it can be completed later.
        for _ in range(200):
            completed_job = do_mail_job(feed_id=feed.feed_id, posts=rss_updates.rss_posts)
            if not completed_job:
                break


def do_feed_job() -> Tuple[Feed, RssUpdates] | Tuple[None, None]:
    """Tries to find a feed in need of a refresh. Returns feed and posts if feed was updated"""
    with QueryManager() as q:
        feed = q.get_feed_to_run()

        if feed is None:
            return None, None

        try:
            posts = caching_get_posts(rss_url=feed.rss_url, last_id=feed.last_post_id, last_date=feed.last_post_pub)
        except Exception:
            q.feed_set_last_fail_now(feed_id=feed.feed_id)
            return None, None

        if len(posts.rss_posts) == 0:
            q.feed_set_last_check_now(feed_id=feed.feed_id)
            return None, None

        feed_update = q.set_feed_update(feed_id=feed.feed_id,
                                        last_post_id=posts.rss_posts[0].post_id,
                                        last_post_pub=posts.rss_posts[0].get_datetime())
        return feed_update, posts


def do_mail_job(feed_id: int, posts: RssUpdates) -> bool:
    """Tries to find subscribers in need of mail under feed id. Returns true if subscribers where found."""
    # It's very important that this context is exited right after fetching the sub.
    # Once it's exited it triggers a commit to the db.
    # If some exception occurs in the block, the transaction will be rolled back.
    # If an exception occurs, we want to be sure there is no retry out of extreme caution of sending duplicate emails
    # I'd rather things fail open in this matter
    with QueryManager() as q:
        sub = q.fetch_and_update_uncurrent_sub(feed_id=feed_id, last_post_id=posts.rss_posts[0].post_id)

    if sub is None:
        with QueryManager() as q:
            q.resolve_feed_notifications(feed_id=feed_id)
        return False

    email_serv.notify_update(to_addr=sub.email, blog_update=posts)
    return True


def find_unfinished_feed() -> Tuple[Feed, RssUpdates] | None:
    """Tries to find any feed with unresolved notifications and returns it along with updates.
    Needed for recovering from worker shutdown during task."""
    with QueryManager() as q:
        feed = q.get_unresolved_feed()

    if not feed:
        return

    posts = caching_get_posts(rss_url=feed.rss_url,
                              last_id=feed.last_notification_post_id,
                              last_date=feed.last_post_pub)

    return feed, posts
