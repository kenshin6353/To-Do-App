# backend/services/user_service/models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from utils.db import Base

class Task(Base):
    __tablename__ = "tasks"
    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer,ForeignKey("users.id", ondelete="CASCADE"),nullable=False,index=True)
    title       = Column(String, nullable=False)
    description = Column(String, nullable=True)
    due_date    = Column(DateTime, nullable=False)
    completed   = Column(Boolean, default=False)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    owner = relationship(
        "User",
        back_populates="tasks",
        lazy="joined"
    )