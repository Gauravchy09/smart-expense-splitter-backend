from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Group(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    base_currency = Column(String, default="USD", nullable=False)
    created_by = Column(Integer, ForeignKey("user.id"), nullable=False) # Owner
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")

class GroupMember(Base):
    group_id = Column(Integer, ForeignKey("group.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    joined_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("Group", back_populates="members")
    user = relationship("User")
