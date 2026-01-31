from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class RecurringExpense(Base):
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("group.id"), nullable=False)
    payer_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD", nullable=False)
    category = Column(String, default="Others", nullable=False)
    frequency = Column(String, nullable=False) # daily, weekly, monthly, yearly
    next_spawn_date = Column(DateTime, default=datetime.utcnow)
    last_spawned_at = Column(DateTime, nullable=True)
    status = Column(String, default="active") # active, paused
    splits = Column(JSON, nullable=False) # Store splits as JSON for simplicity in template
    created_at = Column(DateTime, default=datetime.utcnow)
