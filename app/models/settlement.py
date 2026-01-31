from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Settlement(Base):
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("group.id"), nullable=False)
    payer_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    payee_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD", nullable=False)
    status = Column(String, default="pending") # pending, completed
    created_at = Column(DateTime, default=datetime.utcnow)

    payer = relationship("User", foreign_keys=[payer_id])
    payee = relationship("User", foreign_keys=[payee_id])
