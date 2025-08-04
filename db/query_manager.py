import os
from sqlalchemy.ext.asyncio import create_async_engine
from .sqlc.queries import AsyncQuerier


_DB_USER = os.environ['user']
_DB_PASS = os.environ['password']
_DB_HOST = os.environ['host']
_DB_PORT = os.environ['port']
_DB_DATABASE = os.environ['database']
engine = create_async_engine(url=f"postgresql+asyncpg://{_DB_USER}:{_DB_PASS}@{_DB_HOST}:{_DB_PORT}/{_DB_DATABASE}")


class QueryManager:
    def __init__(self):
        pass

    def __enter__(self):
        raise Exception("Entered without async!")

    async def __aenter__(self) -> AsyncQuerier:
        self.conn = await engine.connect()
        await self.conn.begin()
        return AsyncQuerier(self.conn)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.conn.rollback()
            await self.conn.close()
            return
        await self.conn.commit()
        await self.conn.close()
