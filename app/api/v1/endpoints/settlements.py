from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.crud import crud_settlement
from app.models.user import User

from app.schemas import settlement as settlement_schema
from app.services import notification_service

router = APIRouter()

@router.post("/", response_model=settlement_schema.Settlement)
async def create_settlement(
    *,
    db: AsyncSession = Depends(deps.get_db),
    settlement_in: settlement_schema.SettlementCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Record a payment between users.
    """
    # Simply record the payment
    settlement = await crud_settlement.create_settlement(db=db, settlement=settlement_in)
    
    # Notify the payee
    await notification_service.create_notification(
        db,
        user_id=settlement.payee_id,
        message=f"{current_user.username} recorded a payment of {settlement.currency} {settlement.amount} to you.",
        type="settlement"
    )
    
    return settlement

@router.get("/group/{group_id}", response_model=list[settlement_schema.Settlement])
async def get_group_settlements(
    group_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get settlement history for a group.
    """
    settlements = await crud_settlement.get_settlements_by_group(db=db, group_id=group_id)
    return settlements
