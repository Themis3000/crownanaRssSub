"""
Currently just serves as a test file.

Once all procedures are in place and fully unit tested, a http server with endpoints linked to the procedures will be
stood up in this file
"""
from db import update_db, engine

conn = engine.connect()
update_db(conn)
conn.commit()
conn.close()
