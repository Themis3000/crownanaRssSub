import os
from sqlalchemy import create_engine
from .sqlc.queries import Querier


_DB_USER = os.environ['user']
_DB_PASS = os.environ['password']
_DB_HOST = os.environ['host']
_DB_PORT = os.environ['port']
_DB_DATABASE = os.environ['database']
engine = create_engine(url=f"postgresql+psycopg2://{_DB_USER}:{_DB_PASS}@{_DB_HOST}:{_DB_PORT}/{_DB_DATABASE}")


class QueryManager:
    def __init__(self):
        pass

    def __enter__(self) -> Querier:
        self.conn = engine.connect()
        return Querier(self.conn)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
            self.conn.close()
            return
        self.conn.commit()
        self.conn.close()
