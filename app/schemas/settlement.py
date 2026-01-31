from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import User

class SettlementBase(BaseModel):
    group_id: int
    payer_id: int
    payee_id: int
    amount: float
    currency: str = "USD"
    status: str = "completed"

class SettlementCreate(SettlementBase):
    pass

class Settlement(SettlementBase):
    id: int
    created_at: datetime
    payer: Optional[User] = None
    payee: Optional[User] = None

    class Config:
        from_attributes = True
