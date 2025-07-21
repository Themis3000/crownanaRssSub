from sqlalchemy import create_engine, String, Text, select, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Session, mapped_column, Mapped, Session, relationship
import os
import utils
from datetime import datetime
from typing import Optional

DB_USER = os.environ['user']
DB_PASS = os.environ['password']
DB_HOST = os.environ['host']
DB_PORT = os.environ['port']
DB_DATABASE = os.environ['database']
engine = create_engine(url=f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}")


class Base(DeclarativeBase):
    pass


class Feeds(Base):
    __tablename__ = "feeds"
    feed_id: Mapped[int] = mapped_column(primary_key=True)
    rss_url: Mapped[str] = mapped_column(String(2000))
    feed_name: Mapped[str] = mapped_column(String(2000))
    addition_date: Mapped[datetime] = mapped_column(default="NOW()")


def add_feed(rss_url: str):
    feed = utils.get_posts(rss_url)
    if feed is None:
        raise Exception("Could not fetch posts")
    if len(feed.rss_posts) == 0:
        raise Exception("Post history is empty")
    last_post = feed.rss_posts[0]
    # cursor = conn.cursor()
    # cursor.execute("""
    #     INSERT INTO feeds (rss_url, feed_name, last_post_id, last_post_pub)
    #     VALUES (%(rss_url)s, %(feed_name)s, %(last_post_id)s, %(last_post_pub)s)
    # """, {"rss_url": rss_url, "feed_name": feed.blog_name, "last_post_id": last_post.post_id,
    #       "last_post_pub": last_post.get_datetime()})
    # cursor.close()
    # conn.commit()


def get_feed_by_rss(rss_url: str):
    return
    # cursor = conn.cursor()
    # cursor.execute("""
    #     SELECT feed_id, rss_url, feed_name, addition_date, interval, last_completed, last_update, last_post_id,
    #     last_post_pub, next_run
    #     FROM feeds
    #     WHERE rss_url = %(rss_url)s
    # """, {"rss_url": rss_url})
    # content = cursor.fetchone()
    # cursor.close()
    # return content
