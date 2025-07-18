import unittest
from utils import get_posts
from multiprocessing import Process
import os
import email.utils


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
        newest_post_id = "6c87aa676f44b6cc2dffd176c775263572e523c5"
        newest_post_date = email.utils.parsedate_to_datetime("Mon, 30 Jun 2025 23:00:00 -0600")
        posts = get_posts("http://127.0.0.1:8010/feed1.xml", newest_post_id, newest_post_date)
        self.assertEqual(len(posts.rss_posts), 0)

    def test_feed1_2_new_post(self):
        newest_post_id = "80c0f3f8ff360b14b2ea9a617b290827efbb94dc"
        newest_post_date = email.utils.parsedate_to_datetime("Tue, 27 May 2025 23:00:00 -0600")
        posts = get_posts("http://127.0.0.1:8010/feed1.xml", newest_post_id, newest_post_date)
        self.assertEqual(len(posts.rss_posts), 2)
        self.assertEqual(posts.rss_posts[0].title, "Blog updates")
        self.assertEqual(posts.rss_posts[1].title, "Using photos in Freecad")

    def test_feed1_deleted_post(self):
        newest_post_id = "--invalid id not used by any post--"
        newest_post_date = email.utils.parsedate_to_datetime("Mon, 14 July 2025 23:00:00 -0600")
        posts = get_posts("http://127.0.0.1:8010/feed1.xml", newest_post_id, newest_post_date)
        self.assertEqual(len(posts.rss_posts), 0)

    def test_get_all_feed2_posts(self):
        posts = get_posts("http://127.0.0.1:8010/feed2.xml")
        self.assertEqual(posts.rss_posts[0].title, "7/12/25")
        self.assertEqual(len(posts.rss_posts), 10)
