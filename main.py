"""
Currently just serves as a test file.

Once all procedures are in place and fully unit tested, a http server with endpoints linked to the procedures will be
stood up in this file
"""
from utils import add_subscriber
from db import QueryManager, update_db, engine

conn = engine.connect()
update_db(conn)
conn.commit()
conn.close()

with QueryManager() as q:
    add_subscriber(q=q, rss_url="https://www.crownanabread.com/blog/rss.xml", sub_email="bot@themismegas.com")
