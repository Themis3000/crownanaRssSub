import unittest
from utils import get_posts
from multiprocessing import Process
import os
import email.utils
import rss_db


def start_http():
    from http.server import SimpleHTTPRequestHandler, HTTPServer
    os.chdir("./tests/test_feeds")
    # noinspection PyTypeChecker
    server = HTTPServer(("127.0.0.1", 8010), SimpleHTTPRequestHandler)
    server.serve_forever()


class RssTests(unittest.TestCase):
    """Tests for the utils file"""

    @classmethod
    def setUpClass(cls):
        cls.http_process = Process(target=start_http)
        cls.http_process.start()

    @classmethod
    def tearDownClass(cls):
        cls.http_process.terminate()
        cls.http_process.join()

    def setUp(self):
        cursor = rss_db.conn.cursor()
        cursor.execute("""
            DROP SCHEMA public CASCADE;
            CREATE SCHEMA public;
            GRANT ALL ON SCHEMA public TO postgres;
            GRANT ALL ON SCHEMA public TO public;
            COMMENT ON SCHEMA public IS 'standard public schema';
        """)
        cursor.close()
        rss_db.conn.commit()

    def test_get_all_feed1_posts(self):
        posts = get_posts("http://127.0.0.1:8010/feed1.xml")
        self.assertEqual(posts.rss_posts[0].title, "Blog updates")
        self.assertEqual(len(posts.rss_posts), 3)

    def test_feed1_1_new_post(self):
        second_post_id = "98f0b31174cc026f9a0705df1b168d55672b7832"
        second_post_date = email.utils.parsedate_to_datetime("Mon, 02 Jun 2025 23:00:00 -0600")
        posts = get_posts("http://127.0.0.1:8010/feed1.xml", second_post_id, second_post_date)
        self.assertEqual(posts.rss_posts[0].title, "Blog updates")
        self.assertEqual(len(posts.rss_posts), 1)

    def test_feed1_no_new_post(self):
        post_id = "6c87aa676f44b6cc2dffd176c775263572e523c5"
        post_date = email.utils.parsedate_to_datetime("Mon, 30 Jun 2025 23:00:00 -0600")
        posts = get_posts("http://127.0.0.1:8010/feed1.xml", post_id, post_date)
        self.assertEqual(len(posts.rss_posts), 0)

    def test_feed1_2_new_post(self):
        post_id = "80c0f3f8ff360b14b2ea9a617b290827efbb94dc"
        post_date = email.utils.parsedate_to_datetime("Tue, 27 May 2025 23:00:00 -0600")
        posts = get_posts("http://127.0.0.1:8010/feed1.xml", post_id, post_date)
        self.assertEqual(len(posts.rss_posts), 2)
        self.assertEqual(posts.rss_posts[0].title, "Blog updates")
        self.assertEqual(posts.rss_posts[1].title, "Using photos in Freecad")

    def test_feed1_deleted_post(self):
        post_id = "--invalid id not used by any post--"
        post_date = email.utils.parsedate_to_datetime("Mon, 14 July 2025 23:00:00 -0600")
        posts = get_posts("http://127.0.0.1:8010/feed1.xml", post_id, post_date)
        self.assertEqual(len(posts.rss_posts), 0)

    def test_get_all_feed2_posts(self):
        posts = get_posts("http://127.0.0.1:8010/feed2.xml")
        self.assertEqual(posts.rss_posts[0].title, "7/12/25")
        self.assertEqual(len(posts.rss_posts), 10)

    def test_feed2_get_1_new_post(self):
        post_id = "c1a43f870c6f924141ff18b6138f503ddcdb75f7"
        post_date = email.utils.parsedate_to_datetime("Sun, 13 Jul 2025 04:00:53 +0000")
        posts = get_posts("http://127.0.0.1:8010/feed2.xml", post_id, post_date)
        self.assertEqual(posts.rss_posts[0].title, "7/12/25")
        self.assertEqual(len(posts.rss_posts), 1)

    def test_feed2_no_new_post(self):
        post_id = "92b220bab408cb4d3e4f0b8b788139df4845cfb5"
        post_date = email.utils.parsedate_to_datetime("Sun, 13 Jul 2025 04:08:07 +0000")
        posts = get_posts("http://127.0.0.1:8010/feed2.xml", post_id, post_date)
        self.assertEqual(len(posts.rss_posts), 0)
