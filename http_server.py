from datetime import timedelta
from email_validator import EmailUndeliverableError, EmailSyntaxError
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.exc import IntegrityError
from db import update_db, engine
from utils import (add_subscriber, confirm_subscription, InvalidSubscriber, InvalidConfirmationCode,
                   remove_subscription, update_sub_interval, validate_subscriber)
from db import QueryManager
from typing import Annotated

conn = engine.connect()
update_db(conn)
conn.commit()
conn.close()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


with open("./static/home.html", "r") as f:
    landing_html = f.read()


@app.get("/")
def get_home():
    return HTMLResponse(content=landing_html, status_code=200)


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
    except (EmailUndeliverableError, EmailSyntaxError):
        return templates.TemplateResponse(request=request,
                                          name="signup_failure.jinja2",
                                          context={"error_explanation": f"The email you submitted ({email}) seems to "
                                                                        f"be invalid."},
                                          status_code=400)
    return templates.TemplateResponse(request=request,
                                      name="signup_success.jinja2",
                                      context={"email": email,
                                               "period": notification_delta.days,
                                               "blog_name": feed.feed_name},
                                      status_code=201)


@app.get("/sub_confirm")
def confirm_sub(sub_id: int, code: float, request: Request):
    with QueryManager() as q:
        try:
            # See if I can get sqlc to consider this param as a float in the generated code.
            # noinspection PyTypeChecker
            sub = confirm_subscription(q=q, subscriber_id=sub_id, confirmation_code=code)
        except InvalidSubscriber:
            return templates.TemplateResponse(request=request,
                                              name="confirm_failure.jinja2",
                                              context={"error_explanation": "Invalid subscriber id provided."})
        except InvalidConfirmationCode:
            return templates.TemplateResponse(request=request,
                                              name="confirm_failure.jinja2",
                                              context={"error_explanation": "Invalid confirmation code provided."})

    return templates.TemplateResponse(request=request,
                                      name="confirm_success.jinja2",
                                      context={"email": sub.email, "period": sub.notification_interval.days})


@app.get("/unsubscribe")
def unsub(sub_id: int, code: float, request: Request):
    with QueryManager() as q:
        try:
            sub, feed = remove_subscription(q=q, subscriber_id=sub_id, confirmation_code=code)
        except InvalidSubscriber:
            return templates.TemplateResponse(request=request,
                                              name="unsub_failure.jinja2",
                                              context={"error_explanation": "Invalid subscriber id provided."})
        except InvalidConfirmationCode:
            return templates.TemplateResponse(request=request,
                                              name="unsub_failure.jinja2",
                                              context={"error_explanation": "Invalid confirmation code provided."})

    return templates.TemplateResponse(request=request,
                                      name="unsub_success.jinja2",
                                      context={"email": sub.email, "feed_name": feed.feed_name})


@app.get("/notification_options")
def notification_options(sub_id: int, code: float, request: Request):
    with QueryManager() as q:
        try:
            sub = validate_subscriber(q=q, subscriber_id=sub_id, confirmation_code=code)
        except InvalidSubscriber:
            return templates.TemplateResponse(request=request,
                                              name="options_no_access.jinja2",
                                              context={"error_explanation": "Invalid subscriber id provided."})
        except InvalidConfirmationCode:
            return templates.TemplateResponse(request=request,
                                              name="options_no_access.jinja2",
                                              context={"error_explanation": "Invalid confirmation code provided."})
        feed = q.get_feed(feed_id=sub.feed_id)

    return templates.TemplateResponse(request=request,
                                      name="subscription_options.jinja2",
                                      context={
                                          "blog_name": feed.feed_name,
                                          "interval": sub.notification_interval.days,
                                          "sub_id": sub.subscriber_id,
                                          "code": sub.confirmation_code,
                                          "options": [{"text": "1 day", "value": "1d"},
                                                      {"text": "3 days", "value": "3d"},
                                                      {"text": "7 days", "value": "7d"},
                                                      {"text": "30 days", "value": "30d"}]
                                      })


@app.post("/update_interval")
def update_interval(sub_id: Annotated[int, Form()], code: Annotated[float, Form()], interval: Annotated[str, Form()],
                    request: Request):
    td_interval = timedelta(days=int(interval[:-1]))
    with QueryManager() as q:
        try:
            sub = update_sub_interval(q=q, subscriber_id=sub_id, confirmation_code=code, interval=td_interval)
        except InvalidSubscriber:
            return templates.TemplateResponse(request=request,
                                              name="options_no_access.jinja2",
                                              context={"error_explanation": "Invalid subscriber id provided."})
        except InvalidConfirmationCode:
            return templates.TemplateResponse(request=request,
                                              name="options_no_access.jinja2",
                                              context={"error_explanation": "Invalid confirmation code provided."})

    return templates.TemplateResponse(request=request,
                                      name="options_update_success.jinja2",
                                      context={"email": sub.email,
                                               "interval": td_interval.days})


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8005)
