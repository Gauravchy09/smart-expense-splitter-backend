from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from app.db.base_class import Base

class Notification(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, nullable=False) # expense, settlement, group_invite
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
