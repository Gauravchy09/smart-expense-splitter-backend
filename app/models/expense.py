from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Expense(Base):
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("group.id"))
    payer_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD", nullable=False)
    category = Column(String, default="Others", nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    receipt_image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    splits = relationship("ExpenseSplit", back_populates="expense", cascade="all, delete-orphan")

class ExpenseSplit(Base):
    expense_id = Column(Integer, ForeignKey("expense.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    amount_owed = Column(Float, nullable=False)

    expense = relationship("Expense", back_populates="splits")

    __table_args__ = (
        UniqueConstraint('expense_id', 'user_id', name='unique_expense_user_split'),
    )
