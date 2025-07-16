from rss_parser import RSSParser
import requests
import dataclasses
from typing import List
import hashlib


@dataclasses.dataclass()
class RssPost:
    title: str
    date: str
    description: str
    guid: str = None

    def get_id(self) -> str:
        unique_data = self.guid if self.guid else self.title
        post_hash = hashlib.sha1()
        post_hash.update(unique_data.encode("utf-8"))
        return post_hash.hexdigest()


@dataclasses.dataclass()
class RssUpdates:
    blog_name: str
    rss_posts: List[RssPost]

    def __post_init__(self):
        self.latest_id = self.rss_posts[0].get_id()


def get_posts(rss_url: str, last_id: str) -> RssUpdates | None:
    try:
        response = requests.get(rss_url)
    except requests.exceptions.RequestException:
        return None
    if not response.ok:
        return None

    rss = RSSParser.parse(response.text)
    for item in rss.channel.items:
        pass
