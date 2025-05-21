from datetime import datetime, timedelta
from utils.db import SessionLocal
from services.user_service.models import User
from services.task_service.models import Task
from services.notification_service.models import Notification
from services.notification_service.mailer import send_email
from services.notification_service.logic import get_overdue

# 1. Setup DB session
db = SessionLocal()

# 2. Ensure a test user exists
user = db.query(User).first()
if not user:
    user = User(email="kenshin6353@gmail.com", name="Test User")
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"[✅] Created test user: {user.email}")
else:
    print(f"[✅] Using existing user: {user.email}")

# 3. Add an overdue task
task = Task(
    title="Test Overdue Task",
    due_date=datetime.utcnow() - timedelta(hours=2),
    completed=False,
    user_id=user.id
)
db.add(task)
db.commit()
db.refresh(task)
print(f"[✅] Created overdue task: '{task.title}'")

# 4. Run the same logic as the worker manually
overdue_tasks = get_overdue(db)
print(f"[ℹ️] Found {len(overdue_tasks)} overdue task(s).")

for t in overdue_tasks:
    # Skip if already notified
    if db.query(Notification).filter_by(task_id=t.id, notify_type="overdue").first():
        print(f"[⏩] Skipping task '{t.title}' — notification already sent.")
        continue

    # Send the email
    send_email(
        user.email,
        f"Overdue: '{t.title}'",
        f"Your task '{t.title}' was due at {t.due_date.isoformat()} UTC and is now overdue."
    )
    print(f"[📧] Sent email to {user.email} for task '{t.title}'")

    # Save the notification record
    notification = Notification(task_id=t.id, user_id=user.id, notify_type="overdue")
    db.add(notification)
    db.commit()
    print(f"[📝] Notification saved for task ID {t.id}")

db.close()
#