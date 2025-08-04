import datetime
import email_validator
import unittest
import sqlalchemy
from sqlalchemy.exc import IntegrityError
from utils import validate_and_add_feed, add_subscriber, confirm_subscription, remove_subscription, \
    InvalidConfirmationCode, InvalidSubscriber
from rss import get_posts
from multiprocessing import Process
import email.utils
from db import QueryManager, engine, setup_db
from email_service import email_serv, MockEmail
from worker import do_feed_job, do_mail_jobs
from .test_http import start_http, set_mapping, clear_mappings, test_endpoint
from async_tools import sync_list


class RssTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.http_process = Process(target=start_http)
        cls.http_process.start()
        if not test_endpoint():
            if not test_endpoint():
                raise Exception("Http server didn't start")

    @classmethod
    def tearDownClass(cls):
        cls.http_process.terminate()
        cls.http_process.join()

    async def asyncSetUp(self):
        conn = engine.connect()
        await conn.execute(sqlalchemy.text("""
            DROP SCHEMA public CASCADE;
            CREATE SCHEMA public;
            GRANT ALL ON SCHEMA public TO postgres;
            GRANT ALL ON SCHEMA public TO public;
            COMMENT ON SCHEMA public IS 'standard public schema';
        """))
        await setup_db(conn)
        await conn.commit()
        await conn.close()
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

    async def test_add_feed_1(self):
        with QueryManager() as q:
            await validate_and_add_feed(q, "http://127.0.0.1:8010/feed1.xml")
            feed_data = await q.get_feed_by_rss(rss_url="http://127.0.0.1:8010/feed1.xml")
            self.assertEqual(feed_data.feed_name, "Crownanabread Blog")
            self.assertEqual(feed_data.rss_url, "http://127.0.0.1:8010/feed1.xml")
            feed_history = await sync_list(q.get_feed_history(feed_id=feed_data.feed_id, limit=20))
            self.assertEqual(3, len(feed_history))
            self.assertEqual("Blog updates", feed_history[0].title)
            self.assertEqual("Using photos in Freecad", feed_history[1].title)
            self.assertEqual("A new start!", feed_history[2].title)

    async def test_add_feed_2(self):
        with QueryManager() as q:
            await validate_and_add_feed(q, "http://127.0.0.1:8010/feed2.xml")
            feed_data = await q.get_feed_by_rss(rss_url="http://127.0.0.1:8010/feed2.xml")
            self.assertEqual(feed_data.feed_name, "LuvstarKei")
            self.assertEqual(feed_data.rss_url, "http://127.0.0.1:8010/feed2.xml")
            feed_history = await sync_list(q.get_feed_history(feed_id=feed_data.feed_id, limit=20))
            self.assertEqual(10, len(feed_history))
            self.assertEqual("7/12/25", feed_history[0].title)
            self.assertEqual("Hunter Memphis Jr.", feed_history[1].title)
            self.assertEqual("6/9/25", feed_history[-1].title)

    async def test_add_both_feeds(self):
        await self.test_add_feed_1()
        await self.test_add_feed_2()

    def test_unique(self):
        with QueryManager() as q:
            def add_feed():
                validate_and_add_feed(q, "http://127.0.0.1:8010/feed1.xml")
            add_feed()
            self.assertRaises(IntegrityError, add_feed)

    def add_subscriber(self):
        self.assertIsInstance(email_serv, MockEmail, "The email service is not in testing mode!")
        with QueryManager() as q:
            sub, feed = add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@test.com")
            sub_email = email_serv.email_log[0]
            sub_email_call = email_serv.logged_calls[0]
            self.assertEqual(sub_email_call['blog_name'], "Crownanabread Blog")
            confirm_url = f"http://127.0.0.1:8080/sub_confirm?sub_id={sub.subscriber_id}&code={sub.confirmation_code}"
            self.assertEqual(sub_email_call['confirm_url'], confirm_url)
            self.assertEqual(sub_email.subject, "Confirm your subscription to Crownanabread Blog")
            self.assertEqual(sub_email.to, "test@test.com")

    def test_confirm_subscription(self):
        with QueryManager() as q:
            sub, feed = add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@test.com")
            self.assertFalse(sub.signup_confirmed)
            confirm_subscription(q=q, subscriber_id=sub.subscriber_id, confirmation_code=sub.confirmation_code)
            updated_sub = q.get_subscriber(subscriber_id=sub.subscriber_id)
            self.assertTrue(updated_sub.signup_confirmed)

    def test_forbid_double_subscription(self):
        with QueryManager() as q:
            def subscribe():
                add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@test.com")
            subscribe()
            self.assertRaises(IntegrityError, subscribe)
        with QueryManager() as q:
            add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@test.com")
            add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed2.xml", sub_email="test@test.com")
            add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed2.xml", sub_email="test1@test.com")
            add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test1@test.com")

    def test_unsubscribe(self):
        with QueryManager() as q:
            sub, feed = add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@test.com")
            self.assertTrue(q.subscriber_exists(subscriber_id=sub.subscriber_id))
            remove_subscription(q=q, subscriber_id=sub.subscriber_id, confirmation_code=sub.confirmation_code)
            unsub_email = email_serv.email_log[1]
            self.assertEqual(unsub_email.subject, "Crownanabread Blog unsubscribe confirmation")
            self.assertEqual(unsub_email.to, "test@test.com")
            self.assertFalse(q.subscriber_exists(subscriber_id=sub.subscriber_id))

    def test_invalid_unsubscribe(self):
        with QueryManager() as q:
            sub, feed = add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@test.com")

        with QueryManager() as q:
            invalid_code = sub.confirmation_code + 0.001

            def remove_sub_invalid_code():
                remove_subscription(q=q, subscriber_id=sub.subscriber_id, confirmation_code=invalid_code)
            self.assertRaises(InvalidConfirmationCode, remove_sub_invalid_code)

            def remove_sub_invalid_id():
                remove_subscription(q=q, subscriber_id=1337, confirmation_code=sub.confirmation_code)
            self.assertRaises(InvalidSubscriber, remove_sub_invalid_id)

    def test_invalid_email(self):
        with QueryManager() as q:
            def add_sub_invalid():
                add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@fakedomain9023485.com")
            self.assertRaises(email_validator.exceptions_types.EmailUndeliverableError, add_sub_invalid)

    def test_worker_feed_job(self):
        with QueryManager() as q:
            sub, feed = add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@test.com")
            confirm_subscription(q=q, subscriber_id=sub.subscriber_id, confirmation_code=sub.confirmation_code)
        did_job = do_feed_job()
        self.assertFalse(did_job)

        set_mapping("feed1.xml", "feed1_updated.xml")
        with QueryManager() as q:
            q.feed_update_now(rss_url="http://127.0.0.1:8010/feed1.xml")

        did_job = do_feed_job()
        self.assertTrue(did_job)
        
        with QueryManager() as q:
            history = list(q.get_feed_history(feed_id=feed.feed_id, limit=20))
        self.assertEqual("Creative flash photos", history[0].title)
        self.assertEqual("A new start!", history[-1].title)

    def test_worker_mail_job(self):
        with QueryManager() as q:
            sub, feed = add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed1.xml", sub_email="test@test.com")
            confirm_subscription(q=q, subscriber_id=sub.subscriber_id, confirmation_code=sub.confirmation_code)
        set_mapping("feed1.xml", "feed1_updated.xml")
        with QueryManager() as q:
            q.feed_update_now(rss_url="http://127.0.0.1:8010/feed1.xml")
        do_feed_job()
        self.assertFalse(sub.has_notification_pending)
        self.assertGreater(sub.next_notification, datetime.datetime.now())

        job_completed = do_mail_jobs()
        self.assertFalse(job_completed)

        with QueryManager() as q:
            q.sub_notify_now(subscriber_id=sub.subscriber_id)
        job_completed = do_mail_jobs()
        self.assertTrue(job_completed)

        notification_call = email_serv.logged_calls[-1]
        self.assertEqual("test@test.com", notification_call["to_addr"])
        self.assertEqual("Creative flash photos", notification_call["posts"][0].title)

        job_completed = do_mail_jobs()
        self.assertFalse(job_completed)

        with QueryManager() as q:
            sub = q.get_subscriber(subscriber_id=sub.subscriber_id)
        self.assertFalse(sub.has_notification_pending)
        self.assertGreater(sub.next_notification, datetime.datetime.now())

    # Need to add test for multiple updates in single batch.
    def test_worker_multi_mail_job(self):
        subscribers_feed_1 = ["test@test.com", "test1@test.com", "test2@test.com", "test3@test.com", "test4@test.com"]
        subscribers_feed_2 = ["test5@test.com", "test2@test.com", "test6@test.com", "test7@test.com", "test1@test.com"]
        subscribers_feed_3 = ["test5@test.com", "test2@test.com", "test8@test.com", "test9@test.com", "test10@test.com"]
        feed_plan = [{"rss": "http://127.0.0.1:8010/feed1.xml", "subs": subscribers_feed_1},
                     {"rss": "http://127.0.0.1:8010/feed2.xml", "subs": subscribers_feed_2},
                     {"rss": "http://127.0.0.1:8010/feed3.xml", "subs": subscribers_feed_3}]

        with QueryManager() as q:
            for plan in feed_plan:
                for sub_email in plan["subs"]:
                    sub, feed = add_subscriber(q=q, rss_url=plan["rss"], sub_email=sub_email)
                    confirm_subscription(q=q, subscriber_id=sub.subscriber_id, confirmation_code=sub.confirmation_code)
                    q.sub_notify_now(subscriber_id=sub.subscriber_id)
                # Add one that won't ever have its subscription confirmed to test if it'll get updates.
                sub, feed = add_subscriber(q=q, rss_url=plan["rss"], sub_email="nomail@test.com")
                q.sub_notify_now(subscriber_id=sub.subscriber_id)
                # Add one that is confirmed but not ready for notification
                sub, feed = add_subscriber(q=q, rss_url=plan["rss"], sub_email="nowait@test.com")
                confirm_subscription(q=q, subscriber_id=sub.subscriber_id, confirmation_code=sub.confirmation_code)

                q.feed_update_now(rss_url=plan["rss"])

            # Add a feed that won't receive an update
            sub, feed = add_subscriber(q=q, rss_url="http://127.0.0.1:8010/feed4.xml", sub_email="nomail@test.com")
            q.sub_notify_now(subscriber_id=sub.subscriber_id)
            q.feed_update_now(rss_url="http://127.0.0.1:8010/feed4.xml")

        # Update the feeds
        set_mapping("feed1.xml", "feed1_updated.xml")
        set_mapping("feed2.xml", "feed2_updated.xml")
        set_mapping("feed3.xml", "feed3_updated.xml")
        self.assertTrue(do_feed_job())
        self.assertTrue(do_feed_job())
        self.assertTrue(do_feed_job())
        self.assertTrue(do_feed_job())
        self.assertFalse(do_feed_job())

        self.assertTrue(do_mail_jobs())
        self.assertFalse(do_mail_jobs())

        all_emails = set(subscribers_feed_1 + subscribers_feed_2 + subscribers_feed_3
                         + ["nomail@test.com", "nowait@test.com"])
        email_stats = {test_email: {"signup_confirm": 0, "post_notification": 0} for test_email in all_emails}

        for sent_email in email_serv.email_log:
            if sent_email.subject.startswith("New post on "):
                email_stats[sent_email.to]["post_notification"] += 1
                continue
            if sent_email.subject.startswith("Confirm your subscription to "):
                email_stats[sent_email.to]["signup_confirm"] += 1
                continue
            raise Exception("Unexpected email found")

        email_stats_expectation = {
            "nomail@test.com": {"signup_confirm": 4, "post_notification": 0},
            "test@test.com": {"signup_confirm": 1, "post_notification": 1},
            "test1@test.com": {"signup_confirm": 2, "post_notification": 2},
            "test2@test.com": {"signup_confirm": 3, "post_notification": 3},
            "test3@test.com": {"signup_confirm": 1, "post_notification": 1},
            "test4@test.com": {"signup_confirm": 1, "post_notification": 1},
            "test5@test.com": {"signup_confirm": 2, "post_notification": 2},
            "test6@test.com": {"signup_confirm": 1, "post_notification": 1},
            "test7@test.com": {"signup_confirm": 1, "post_notification": 1},
            "test8@test.com": {"signup_confirm": 1, "post_notification": 1},
            "test9@test.com": {"signup_confirm": 1, "post_notification": 1},
            "test10@test.com": {"signup_confirm": 1, "post_notification": 1},
            "nowait@test.com": {"signup_confirm": 3, "post_notification": 0},
        }
        self.assertEqual(email_stats_expectation, email_stats)
