from db import QueryManager
from rss import get_posts
from cachetools import TTLCache, cached


# This isn't friendly to multiple concurrent workers
# Things probably won't break technically speaking, but it will cause duplicate fetches to the rss endpoint
# We don't want to get rate limited or get inconsistent responses...
post_caching = cached(cache=(TTLCache(maxsize=10, ttl=600)))
caching_get_posts = post_caching(get_posts)


# Handles doing work and the priority of what work to do. Will run forever.
def do_work():
    pass


def do_feed_job() -> bool:
    """Tries to find a feed in need of a refresh. Returns if job has been found"""
    with QueryManager as q:
        feed = q.get_feed_to_run()
        posts = caching_get_posts(rss_url=feed.rss_url, last_id=feed.last_post_id, last_date=feed.last_post_pub)

        if len(posts.rss_posts) == 0:
            q.feed_set_last_check_now(feed_id=feed.feed_id)
            return False

        q.set_feed_update(feed_id=feed.feed_id,
                          last_post_id=posts.rss_posts[0].post_id,
                          last_post_pub=posts.rss_posts[0].get_datetime())
        return True


