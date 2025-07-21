import sqlalchemy

with open("./db/sqlc/setup_query.sql", "r") as f:
    setup_query = f.read()


def setup_db(conn: sqlalchemy.engine.Connection):
    conn.execute(sqlalchemy.text(setup_query))


def update_db(conn: sqlalchemy.engine.Connection):
    result = conn.execute(
        sqlalchemy.text("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='feeds');")).fetchone()
    if result[0]:
        return
    setup_db(conn)
