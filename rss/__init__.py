import dataclasses
import email.utils
import hashlib
from datetime import datetime, timezone
from typing import List
import requests
from rss_parser import RSSParser


@dataclasses.dataclass()
class RssPost:
    title: str
    date: str
    description: str
    link: str
    guid: str = None

    def __post_init__(self):
        self.post_id = self._get_id()

    def _get_id(self) -> str:
        unique_data = self.guid if self.guid else self.title
        post_hash = hashlib.sha1()
        post_hash.update(unique_data.encode("utf-8"))
        return post_hash.hexdigest()

    def get_datetime(self) -> datetime:
        try:
            date = email.utils.parsedate_to_datetime(self.date)
        except ValueError:
            # Raised when date format does not conform to rfc822
            # In the future, find some soft way to deal with this that doesn't involve raising an exception.
            raise
        return date

    def get_readable_date(self) -> str:
        date = self.get_datetime()
        return date.strftime("%b %d, $Y")


@dataclasses.dataclass()
class RssUpdates:
    blog_name: str
    rss_posts: List[RssPost]


def get_posts(rss_url: str, last_id: str = None,
              last_date: datetime = datetime(year=1980, month=1, day=1, tzinfo=timezone.utc)) -> RssUpdates | None:
    """Fetches all new posts up to the last known post id"""
    try:
        response = requests.get(rss_url)
    except requests.exceptions.RequestException:
        return None
    if not response.ok:
        return None

    rss = RSSParser.parse(response.text)
    rss_posts: List[RssPost] = []
    for item in rss.channel.items:
        post = RssPost(
            title=item.title.content,
            date=item.pub_date.content,
            description=item.description.content,
            link=item.links[0].content,
            guid=item.guid.content if item.guid else None
        )
        if last_date > post.get_datetime():
            break
        if post.post_id == last_id:  # Just in case the most recent post had its pub time changed (edits made to it?)
            break
        rss_posts.append(post)

    return RssUpdates(blog_name=rss.channel.title.content, rss_posts=rss_posts)
