from cachetools import TTLCache, cached


def get_posts(rss_url: int, other=1):
    return rss_url + other


post_caching = cached(cache=(TTLCache(maxsize=10, ttl=600)), key=lambda **kwargs: kwargs["rss_url"])
caching_get_posts = post_caching(get_posts)


print(caching_get_posts(rss_url=1, other=2))
print(caching_get_posts(rss_url=1, other=5))
print(caching_get_posts(rss_url=2, other=5))
