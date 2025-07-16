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
    link: str
    guid: str = None

    def __post_init__(self):
        self.post_id = self._get_id()

    def _get_id(self) -> str:
        unique_data = self.guid if self.guid else self.title
        post_hash = hashlib.sha1()
        post_hash.update(unique_data.encode("utf-8"))
        return post_hash.hexdigest()


@dataclasses.dataclass()
class RssUpdates:
    blog_name: str
    rss_posts: List[RssPost]


#TODO what if a post is deleted? Do some sort of date check
def get_posts(rss_url: str, last_id: str = None) -> RssUpdates | None:
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
        if post.post_id == last_id:
            break
        rss_posts.append(post)

    return RssUpdates(blog_name=rss.channel.title.content, rss_posts=rss_posts)
