from db import QueryManager
from db.sqlc.models import Feed
from rss import get_posts, RssUpdates
from cachetools import TTLCache, cached
from email_service import email_serv
import time
from utils import store_posts


post_caching = cached(cache=(TTLCache(maxsize=10, ttl=600)))
caching_get_posts = post_caching(get_posts)


# Handles doing work and the priority of what work to do. Will run forever.
def do_work():
    while True:
        did_feed_job = do_feed_job()

        # Do up to 200 mail jobs at a time. If there's more it can be completed later.
        for _ in range(200):
            did_mail_job = do_mail_job()
            if not did_mail_job:
                break

        # noinspection PyUnboundLocalVariable
        if not did_feed_job and not did_mail_job:
            # There is no job to do. Wait 30 seconds before checking again...
            time.sleep(30)
            continue


def do_feed_job() -> bool:
    """Tries to find a feed in need of a refresh. Returns if feed was updated"""
    with QueryManager() as q:
        feed_job = q.get_feed_to_run()

        if feed_job is None:
            return False

        try:
            posts = get_posts(rss_url=feed_job.rss_url, last_id=feed_job.unique_id, last_date=feed_job.post_date)
        except Exception:
            q.feed_set_last_fail_now(feed_id=feed_job.feed_id)
            return False

        if len(posts.rss_posts) == 0:
            q.feed_set_last_check_now(feed_id=feed_job.feed_id)
            return False

        store_posts(q=q, feed_id=feed_job.feed_id, updates=posts)
        q.mark_feed_updates(feed_id=feed_job.feed_id)
        return True


def do_mail_job() -> bool:
    """Tries to find users with a notification due and executes the notification.
    Returns if job was found and completed"""
    with QueryManager() as q:
        sub = q.find_subscriber_to_notify()
        if sub is None:
            return False
        new_posts = list(q.get_feed_history_since_id(feed_id=sub.feed_id, history_id=sub.last_post_notify, limit=20))

    # The length of new_posts should never ever be 0 ever.
    # But if by some miracle it is, it's important this exception is thrown outside of the QueryManager() block.
    # Any exception thrown in an exception manager block will cause a rollback, which would cause an infinite loop
    # as the subscriber would never be marked as notified.
    if len(new_posts) == 0:
        with QueryManager() as q:
            q.mark_subscriber_notified(subscriber_id=sub.subscriber_id, last_post_notify=sub.last_post_notify)
        raise Exception(f"Subscriber {sub.subscriber_id} marked as ready had no new posts actually ready.")

    # I'm marking notified before sending the email. If it fails it's not that big of a deal.
    # I'd rather things fail open in this way.
    with QueryManager() as q:
        q.mark_subscriber_notified(subscriber_id=sub.subscriber_id, last_post_notify=new_posts[-1].history_id)

    email_serv.notify_update(to_addr=sub.email, posts=new_posts, blog_name=sub.feed_name)
    return True
