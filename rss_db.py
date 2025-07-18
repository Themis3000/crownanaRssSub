import psycopg2
from rss_parser import RSSParser
import os

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


cursor = conn.cursor()
cursor.execute("""
SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='feeds');
""")
if not cursor.fetchone()[0]:
    run_setup()
cursor.close()


def add_feed(rss_url: str):
    pass
