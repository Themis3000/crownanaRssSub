"""
Currently just serves as a test file.

Once all procedures are in place and fully unit tested, a http server with endpoints linked to the procedures will be
stood up in this file
"""

from utils import validate_and_add_feed
from db import QueryManager, update_db, engine

conn = engine.connect()
update_db(conn)
conn.commit()
conn.close()

with QueryManager() as q:
    validate_and_add_feed(q, "https://www.crownanabread.com/blog/rss.xml")
    feed_data = q.get_feed_by_rss(rss_url="https://www.crownanabread.com/blog/rss.xml")
    print(feed_data)
