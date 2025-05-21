from celery import Celery
from datetime import datetime
from utils.config import BROKER_URL
from utils.db import engine, Base, SessionLocal
from .models import Notification
from services.user_service.models import User
from services.task_service.models import Task
from .logic import get_due_soon, get_overdue
from .mailer import send_email

# Celery setup
app = Celery("notification_service", broker=BROKER_URL)
app.conf.beat_schedule = {
    "due-soon-every-10": {
        "task": "services.notification_service.worker.due_soon_notify",
        "schedule": 10.0
    },
    "overdue-every-10": {
        "task": "services.notification_service.worker.overdue_notify",
        "schedule": 10.0
    },
}

# ensure notifications table exists
Base.metadata.create_all(bind=engine)

@app.task
def due_soon_notify():
    db = SessionLocal()
    for task in get_due_soon(db):
        # skip if already sent
        if db.query(Notification).filter_by(task_id=task.id, notify_type="due_soon").first():
            continue
        user = db.query(User).get(task.user_id)
        if not user: continue
        send_email(
            user.email,
            f"Reminder: '{task.title}' due soon",
            f"Your task '{task.title}' is due at {task.due_date.isoformat()} UTC."
        )
        db.add(Notification(task_id=task.id, user_id=user.id, notify_type="due_soon"))
        db.commit()
    db.close()

@app.task
def overdue_notify():
    db = SessionLocal()
    for task in get_overdue(db):
        if db.query(Notification).filter_by(task_id=task.id, notify_type="overdue").first():
            continue
        user = db.query(User).get(task.user_id)
        if not user: continue
        send_email(
            user.email,
            f"Overdue: '{task.title}'",
            f"Your task '{task.title}' was due at {task.due_date.isoformat()} UTC and is now overdue."
        )
        db.add(Notification(task_id=task.id, user_id=user.id, notify_type="overdue"))
        db.commit()
    db.close()
