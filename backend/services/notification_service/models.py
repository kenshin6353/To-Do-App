from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from utils.db import Base

class Notification(Base):
    __tablename__ = "notifications"

    id          = Column(Integer, primary_key=True, index=True)
    task_id     = Column(Integer, nullable=False, index=True)
    user_id     = Column(Integer, nullable=False, index=True)
    notify_type = Column(String, nullable=False)  # 'due_soon' or 'overdue'
    sent_at     = Column(DateTime, default=datetime.utcnow)
