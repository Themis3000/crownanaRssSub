import psycopg2
import os
import utils

conn = psycopg2.connect(database=os.environ["database"],
                        host=os.environ["host"],
                        user=os.environ["user"],
                        password=os.environ["password"],
                        port=int(os.environ["port"]))

with open("setup_query.sql", "r") as f:
    setup_query = f.read()


def run_setup():
    cursor = conn.cursor()
    cursor.execute(setup_query)
    cursor.close()
    conn.commit()


setup_cursor = conn.cursor()
setup_cursor.execute("""
SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='feeds');
""")
if not setup_cursor.fetchone()[0]:
    run_setup()
setup_cursor.close()


def add_feed(rss_url: str):
    feed = utils.get_posts(rss_url)
    if feed is None:
        raise Exception("Could not fetch posts")
    if len(feed.rss_posts) == 0:
        raise Exception("Post history is empty")
    last_post = feed.rss_posts[0]
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO feeds (rss_url, feed_name, last_post_id, last_post_pub)
        VALUES (%(rss_url)s, %(feed_name)s, %(last_post_id)s, %(last_post_pub)s)
    """, {"rss_url": rss_url, "feed_name": feed.blog_name, "last_post_id": last_post.post_id,
          "last_post_pub": last_post.get_datetime()})
    cursor.close()
    conn.commit()
