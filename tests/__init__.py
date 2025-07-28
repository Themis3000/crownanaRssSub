import unittest
import sqlalchemy
from multiprocessing import Process
from db import engine, setup_db
from email_service import email_serv
from test_http import start_http, set_mapping, clear_mappings


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
