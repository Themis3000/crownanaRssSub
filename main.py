from fastapi import FastAPI, Response
import uvicorn
from db import update_db, engine

conn = engine.connect()
update_db(conn)
conn.commit()
conn.close()

app = FastAPI()


@app.post("/signup")
def register_sub():
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8005)
