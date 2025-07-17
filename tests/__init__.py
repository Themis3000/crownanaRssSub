import unittest
import subprocess
from utils import get_posts
from multiprocessing import Process


class RssTests(unittest.TestCase):
    """Tests for the utils file"""

    @classmethod
    def setUpClass(cls):
        def start_http():
            subprocess.run(["python", "-m", "http.server", "-d", "./tests/test_feeds", "9870"])

        cls.http_process = Process(target=start_http)
        cls.http_process.start()

    @classmethod
    def tearDownClass(cls):
        cls.http_process.kill()

    def get_all_feed1_posts(self):
        posts = get_posts("http://localhost:9870/feed1.xml")
        print(posts)
        self.assertTrue(posts.rss_posts[0].title == "Blog updates")
