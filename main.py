import rss_db
from utils import get_posts

posts = get_posts("http://localhost:8080/blog/rss.xml")
print(posts)
