from datetime import datetime, timedelta
from services.task_service.models import Task
from services.user_service.models import User
from utils.db import SessionLocal
from .models import Notification

def get_due_soon(session):
    now = datetime.utcnow() + timedelta(hours=7)
    in_one_hour = now + timedelta(hours=1)
    return session.query(Task).filter(
        Task.completed == False,
        Task.due_date >= now,
        Task.due_date <= in_one_hour
    ).all()

def get_overdue(session):
    now = datetime.utcnow() + timedelta(hours=7)
    return session.query(Task).filter(
        Task.completed == False,
        Task.due_date < now
    ).all()
