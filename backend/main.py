# import smtplib

# sender = "Private Person <hello@demomailtrap.co>"
# receiver = "A Test User <kenshin6353@gmail.com>"

# message = f"""\
# Subject: Hi Mailtrap
# To: {receiver}
# From: {sender}

# This is a test e-mail message."""

# with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
#     server.starttls()
#     server.login("api", "9c5a80bce56069859d743a438f9f5080")
#     server.sendmail(sender, receiver, message)


# from utils.db import SessionLocal
# from services.user_service.models import User
# from services.task_service.models import Task

# from datetime import datetime, timezone

# db = SessionLocal()
# tasks = db.query(Task).order_by(Task.due_date.desc()).limit(3).all()
# now = datetime.now(timezone.utc)

# for task in tasks:
#     print(f"Task: {task.title} | Due Date: {task.due_date} | Now UTC: {now}")


from utils.db import SessionLocal
from services.notification_service.models import Notification
from datetime import datetime

# Open a DB session
db = SessionLocal()

# Query all notifications
notifications = db.query(Notification).order_by(Notification.sent_at.desc()).all()

# Display results
print(f"\n[📋] Found {len(notifications)} notification(s):\n")

for n in notifications:
    print(f"📝 Notification ID: {n.id}")
    print(f"    Task ID      : {n.task_id}")
    print(f"    User ID      : {n.user_id}")
    print(f"    Type         : {n.notify_type}")
    print(f"    Sent At      : {n.sent_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print("")

# Close session
db.close()
