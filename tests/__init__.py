import unittest
import email_validator.exceptions_types
import sqlalchemy
from utils import validate_and_add_feed, add_subscriber, confirm_subscription, remove_subscription, \
    InvalidConfirmationCode, InvalidSubscriber
from rss import get_posts
from multiprocessing import Process
import email.utils
from db import QueryManager, engine, setup_db
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from email_service import email_serv, MockEmail
from worker import do_feed_job, find_unfinished_feed, do_mail_job
from .test_http import start_http, set_mapping, clear_mappings


class RssTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http_process = Process(target=start_http)
        cls.http_process.start()

    @classmethod
    def tearDownClass(cls):
        cls.http_process.terminate()
        cls.http_process.join()

    def setUp(self):
        conn = engine.connect()
        conn.execute(sqlalchemy.text("""
            DROP SCHEMA public CASCADE;
            CREATE SCHEMA public;
            GRANT ALL ON SCHEMA public TO postgres;
            GRANT ALL ON SCHEMA public TO public;
            COMMENT ON SCHEMA public IS 'standard public schema';
        """))
        setup_db(conn)
        conn.commit()
        conn.close()
        email_serv.clear_logs()
        clear_mappings()

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

    def test_add_feed_1(self):
        with QueryManager() as q:
            validate_and_add_feed(q, "http://127.0.0.1:8010/feed1.xml")
            feed_data = q.get_feed_by_rss(rss_url="http://127.0.0.1:8010/feed1.xml")
            self.assertEqual(feed_data.feed_name, "Crownanabread Blog")
            self.assertEqual(feed_data.rss_url, "http://127.0.0.1:8010/feed1.xml")
            # Need to also validate stored history too.

    # def test_add_feed_2(self):
    #     with QueryManager() as q:
    #         validate_and_add_feed(q, "http://127.0.0.1:8010/feed2.xml")
    #         feed_data = q.get_feed_by_rss(rss_url="http://127.0.0.1:8010/feed2.xml")
    #         self.assertEqual(feed_data.feed_name, "LuvstarKei")
    #         self.assertEqual(feed_data.rss_url, "http://127.0.0.1:8010/feed2.xml")
    #         self.assertEqual(feed_data.last_post_pub, datetime(2025, 7, 13, 4, 8, 7,
    #                                                            tzinfo=timezone.utc))
    #         self.assertEqual(feed_data.last_post_id, '92b220bab408cb4d3e4f0b8b788139df4845cfb5')
    #
    # def test_unique(self):
    #     with QueryManager() as q:
    #         def add_feed():
    #             validate_and_add_feed(q, "http://127.0.0.1:8010/feed1.xml")
    #         add_feed()
    #         self.assertRaises(IntegrityError, add_feed)
    #
    # def test_add_subscriber(self):
    #     if not isinstance(email_serv, MockEmail):
    #         raise Exception("The email service is not in testing mode.")
    #
    #     with QueryManager() as q:
    #         sub = add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@test.com")
    #         sub_email = email_serv.email_log[0]
    #         sub_email_call = email_serv.logged_calls[0]
    #         self.assertEqual(sub_email_call['blog_name'], "Crownanabread Blog")
    #         confirm_url = f"http://127.0.0.1:8080/sub_confirm?sub_id={sub.subscriber_id}&code={sub.confirmation_code}"
    #         self.assertEqual(sub_email_call['confirm_url'], confirm_url)
    #         self.assertEqual(sub_email.subject, "Confirm your subscription to Crownanabread Blog")
    #         self.assertEqual(sub_email.to, "test@test.com")
    #
    # def test_confirm_subscription(self):
    #     with QueryManager() as q:
    #         sub = add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@test.com")
    #         self.assertFalse(sub.signup_confirmed)
    #         confirm_subscription(q=q, subscriber_id=sub.subscriber_id, confirmation_code=sub.confirmation_code)
    #         updated_sub = q.get_subscriber(subscriber_id=sub.subscriber_id)
    #         self.assertTrue(updated_sub.signup_confirmed)
    #
    # def test_forbid_double_subscription(self):
    #     with QueryManager() as q:
    #         def subscribe():
    #             add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@test.com")
    #         subscribe()
    #         self.assertRaises(IntegrityError, subscribe)
    #     with QueryManager() as q:
    #         add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@test.com")
    #         add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed2.xml", sub_email="test@test.com")
    #         add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed2.xml", sub_email="test1@test.com")
    #         add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test1@test.com")
    #
    # def test_unsubscribe(self):
    #     with QueryManager() as q:
    #         sub = add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@test.com")
    #         self.assertTrue(q.subscriber_exists(subscriber_id=sub.subscriber_id))
    #         remove_subscription(q=q, subscriber_id=sub.subscriber_id, confirmation_code=sub.confirmation_code)
    #         unsub_email = email_serv.email_log[1]
    #         self.assertEqual(unsub_email.subject, "Crownanabread Blog unsubscribe confirmation")
    #         self.assertEqual(unsub_email.to, "test@test.com")
    #         self.assertFalse(q.subscriber_exists(subscriber_id=sub.subscriber_id))
    #
    # def test_invalid_unsubscribe(self):
    #     with QueryManager() as q:
    #         sub = add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@test.com")
    #
    #     with QueryManager() as q:
    #         invalid_code = sub.confirmation_code + 0.001
    #
    #         def remove_sub_invalid_code():
    #             remove_subscription(q=q, subscriber_id=sub.subscriber_id, confirmation_code=invalid_code)
    #         self.assertRaises(InvalidConfirmationCode, remove_sub_invalid_code)
    #
    #         def remove_sub_invalid_id():
    #             remove_subscription(q=q, subscriber_id=1337, confirmation_code=sub.confirmation_code)
    #         self.assertRaises(InvalidSubscriber, remove_sub_invalid_id)
    #
    # def test_invalid_email(self):
    #     with QueryManager() as q:
    #         def add_sub_invalid():
    #             add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@fakedomain9023485.com")
    #         self.assertRaises(email_validator.exceptions_types.EmailUndeliverableError, add_sub_invalid)
    #
    # def test_worker_feed_job(self):
    #     with QueryManager() as q:
    #         sub = add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@test.com")
    #         confirm_subscription(q=q, subscriber_id=sub.subscriber_id, confirmation_code=sub.confirmation_code)
    #     feed, rss_updates = do_feed_job()
    #     self.assertIsNone(feed)
    #
    #     set_mapping("feed1.xml", "feed1_updated.xml")
    #     with QueryManager() as q:
    #         q.feed_update_now(rss_url="http://127.0.0.1:8010/feed1.xml")
    #
    #     feed, rss_updates = do_feed_job()
    #     self.assertIsNotNone(feed)
    #     self.assertIsNotNone(rss_updates)
    #
    # def test_worker_mail_job(self):
    #     with QueryManager() as q:
    #         sub = add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@test.com")
    #         confirm_subscription(q=q, subscriber_id=sub.subscriber_id, confirmation_code=sub.confirmation_code)
    #     set_mapping("feed1.xml", "feed1_updated.xml")
    #     with QueryManager() as q:
    #         q.feed_update_now(rss_url="http://127.0.0.1:8010/feed1.xml")
    #
    #     feed, rss_updates = do_feed_job()
    #     self.assertTrue(feed.unresolved_notification)
    #     job_completed = do_mail_job(feed_id=feed.feed_id, posts=rss_updates)
    #     self.assertTrue(job_completed)
    #
    #     notification_call = email_serv.logged_calls[-1]
    #     self.assertEqual("test@test.com", notification_call["to_addr"])
    #     self.assertEqual(rss_updates, notification_call["blog_update"])
    #
    #     job_completed = do_mail_job(feed_id=feed.feed_id, posts=rss_updates)
    #     self.assertFalse(job_completed)
    #     with QueryManager() as q:
    #         feed = q.get_feed(feed_id=feed.feed_id)
    #     self.assertFalse(feed.unresolved_notification)
    #
    # def test_find_unfinished_feed(self):
    #     with QueryManager() as q:
    #         sub = add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@test.com")
    #         confirm_subscription(q=q, subscriber_id=sub.subscriber_id, confirmation_code=sub.confirmation_code)
    #     set_mapping("feed1.xml", "feed1_updated.xml")
    #     with QueryManager() as q:
    #         q.feed_update_now(rss_url="http://127.0.0.1:8010/feed1.xml")
    #     do_feed_job()
    #
    #     feed, rss_updates = find_unfinished_feed()
    #     self.assertIsNotNone(feed)
    #     self.assertEqual("http://127.0.0.1:8010/feed1.xml", feed.rss_url)
    #     self.assertTrue(feed.unresolved_notification)
    #     self.assertEqual("Creative flash photos", rss_updates.rss_posts[0].title)
    #     self.assertEqual(1, len(rss_updates.rss_posts))
