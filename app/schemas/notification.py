from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class NotificationBase(BaseModel):
    message: str
    type: str
    is_read: bool = False

class Notification(NotificationBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
