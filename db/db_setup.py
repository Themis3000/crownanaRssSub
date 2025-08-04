import sqlalchemy
from sqlalchemy.ext.asyncio.engine import AsyncConnection

with open("./db/sqlc/setup_query.sql", "r") as f:
    setup_query = f.read()


async def setup_db(conn: AsyncConnection):
    await conn.execute(sqlalchemy.text(setup_query))


async def update_db(conn: AsyncConnection):
    result = (await conn.execute(
        sqlalchemy.text("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='feeds');"))).fetchone()
    if result[0]:
        return
    await setup_db(conn)
