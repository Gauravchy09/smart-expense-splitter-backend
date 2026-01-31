from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    base_currency: str = "USD"

class GroupCreate(GroupBase):
    pass

class GroupUpdate(GroupBase):
    pass

from app.schemas.user import User

class GroupMemberBase(BaseModel):
    user_id: int
    role: str = "member"

class GroupMember(GroupMemberBase):
    user: Optional[User] = None

    class Config:
        from_attributes = True

class GroupInDBBase(GroupBase):
    id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True

class Group(GroupInDBBase):
    members: List[GroupMember] = []
