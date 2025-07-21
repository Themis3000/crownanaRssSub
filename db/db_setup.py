import sqlalchemy

with open("./db/sqlc/setup_query.sql", "r") as f:
    setup_query = f.read()


def setup_db(conn: sqlalchemy.engine.Connection):
    conn.execute(sqlalchemy.text(setup_query))
