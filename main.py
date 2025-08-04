from datetime import timedelta
from email_validator import EmailUndeliverableError
from fastapi import FastAPI, Response, Request, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from db import update_db, engine
from utils import add_subscriber
from db import QueryManager
from typing import Annotated

conn = engine.connect()
update_db(conn)
conn.commit()
conn.close()

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.post("/signup")
def register_sub(rss_url: Annotated[str, Form()], email: Annotated[str, Form()],
                 notification_period: Annotated[str, Form()], request: Request):
    notification_delta = timedelta(days=int(notification_period[:-1]))
    try:
        with QueryManager() as q:
            sub, feed = add_subscriber(q=q, rss_url=rss_url, sub_email=email, notification_delta=notification_delta)
    except IntegrityError:
        # Should check if they haven't confirmed the subscription yet.
        # If they haven't, have the ability to resend.
        return templates.TemplateResponse(request=request,
                                          name="signup_failure.jinja2",
                                          context={"error_explanation": "You're already signed up for notifications "
                                                                        "from this site!"},
                                          status_code=400)
    except EmailUndeliverableError:
        return templates.TemplateResponse(request=request,
                                          name="signup_failure.jinja2",
                                          context={"error_explanation": f"The email you submitted {email} seems to "
                                                                        f"be invalid."},
                                          status_code=400)
    return templates.TemplateResponse(request=request,
                                      name="signup_success.jinja2",
                                      context={"email": email,
                                               "period": notification_delta.days,
                                               "blog_name": feed.feed_name},
                                      status_code=201)


@app.get("/sub_confirm")
def confirm_sub(sub_id: int, code: int):
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)
