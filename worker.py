import datetime
from typing import List
from db import QueryManager
from db.sqlc.models import FeedHistory
from db.sqlc.queries import find_notify_mark_updating_subsRow
from rss import get_posts
from functools import lru_cache
from email_service import email_serv
import time
from utils import store_posts


# Handles doing work and the priority of what work to do. Will run forever.
def do_work():
    while True:
        # Update a single feed if one is ready.
        did_feed_job = do_feed_job()

        # Do up to 200 mail jobs at a time. If there's more it can be completed later.
        did_mail_job = do_mail_jobs(limit=200)

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


def do_mail_jobs(limit=100) -> bool:
    """Tries to find users with a notification due and executes the notification.
    Returns if job was found and completed"""
    with QueryManager() as q:
        subs = list(q.find_notify_mark_updating_subs(limit=limit))
        if len(subs) == 0:
            return False

    @lru_cache(maxsize=128)
    def caching_get_feed_history_since_id(feed_id: int, history_id: int, history_limit: int) -> List[FeedHistory]:
        with QueryManager() as q:
            return list(q.get_feed_history_since_id(feed_id=feed_id, history_id=history_id, limit=history_limit))

    for sub in subs:
        # If coming up on the 5 minute limit to complete the batch, stop early to ensure no double emails.
        if sub.last_process_update + datetime.timedelta(minutes=4, seconds=30) < datetime.datetime.now():
            break

        post_history = caching_get_feed_history_since_id(feed_id=sub.feed_id,
                                                         history_id=sub.last_post_notify,
                                                         history_limit=20)

        send_mail_notification(sub=sub, post_history=post_history)

    return True


def send_mail_notification(sub: find_notify_mark_updating_subsRow, post_history: List[FeedHistory]):
    # The length of new_posts should never ever be 0.
    # But just in case, mark as notified anyway and move on.
    if len(post_history) == 0:
        with QueryManager() as q:
            q.mark_subscriber_notified(subscriber_id=sub.subscriber_id, last_post_notify=sub.last_post_notify)
        return

    # I'm marking notified before sending the email. If it fails it's not that big of a deal.
    # I'd rather things fail open in this way.
    with QueryManager() as q:
        q.mark_subscriber_notified(subscriber_id=sub.subscriber_id, last_post_notify=post_history[-1].history_id)

    email_serv.notify_update(to_addr=sub.email, posts=post_history, blog_name=sub.feed_name)
