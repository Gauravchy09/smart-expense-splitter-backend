from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class RecurringExpenseBase(BaseModel):
    group_id: int
    payer_id: int
    description: str
    amount: float
    currency: str = "USD"
    category: str = "General"
    frequency: str # daily, weekly, monthly, yearly
    status: str = "active"
    splits: List[dict]

class RecurringExpenseCreate(RecurringExpenseBase):
    pass

class RecurringExpenseUpdate(BaseModel):
    status: Optional[str] = None
    amount: Optional[float] = None
    frequency: Optional[str] = None

class RecurringExpense(RecurringExpenseBase):
    id: int
    next_spawn_date: datetime
    last_spawned_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
