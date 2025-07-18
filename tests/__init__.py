import time
import unittest
from utils import get_posts
from multiprocessing import Process
import requests
import os


def start_http():
    from http.server import SimpleHTTPRequestHandler, HTTPServer
    os.chdir("./tests/test_feeds")
    # noinspection PyTypeChecker
    server = HTTPServer(("localhost", 8010), SimpleHTTPRequestHandler)
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
        posts = get_posts("http://localhost:8010/feed1.xml")
        print(posts)
        self.assertTrue(posts.rss_posts[0].title == "Blog updates")
