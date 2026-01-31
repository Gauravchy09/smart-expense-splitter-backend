from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class ExpenseSplitBase(BaseModel):
    user_id: int
    amount_owed: float

class ExpenseBase(BaseModel):
    description: str
    amount: float
    currency: str = "USD"
    category: str = "Others"
    date: Optional[datetime] = None

class ExpenseCreate(ExpenseBase):
    group_id: int
    splits: List[ExpenseSplitBase]

class Expense(ExpenseBase):
    id: int
    group_id: int
    payer_id: int
    receipt_image_url: Optional[str] = None
    created_at: datetime
    splits: List[ExpenseSplitBase] = []
    
    class Config:
        from_attributes = True
