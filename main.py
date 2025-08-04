from datetime import timedelta

from fastapi import FastAPI, Response
from db import update_db, engine
from utils import add_subscriber
from db import QueryManager

conn = engine.connect()
update_db(conn)
conn.commit()
conn.close()

app = FastAPI()


@app.post("/signup")
def register_sub(rss_url: str, email: str, notification_period: str):
    notification_delta = timedelta(days=int(notification_period[:-1]))
    with QueryManager() as q:
        add_subscriber(q=q, rss_url=rss_url, sub_email=email, notification_delta=notification_delta)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)
