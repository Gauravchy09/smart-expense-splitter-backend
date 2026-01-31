from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.models.user import User
from app.models.recurring_expense import RecurringExpense
from app.schemas import recurring_expense as schemas
from app.services import recurring_service

router = APIRouter()

@router.post("/", response_model=schemas.RecurringExpense)
async def create_recurring_expense(
    *,
    db: AsyncSession = Depends(deps.get_db),
    re_in: schemas.RecurringExpenseCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new recurring expense.
    """
    db_re = RecurringExpense(
        group_id=re_in.group_id,
        payer_id=re_in.payer_id,
        description=re_in.description,
        amount=re_in.amount,
        currency=re_in.currency,
        category=re_in.category,
        frequency=re_in.frequency,
        status=re_in.status,
        splits=re_in.splits
    )
    db.add(db_re)
    await db.commit()
    await db.refresh(db_re)
    return db_re

@router.get("/group/{group_id}", response_model=List[schemas.RecurringExpense])
async def get_group_recurring_expenses(
    group_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get all recurring expenses for a group.
    """
    result = await db.execute(
        select(RecurringExpense).filter(RecurringExpense.group_id == group_id)
    )
    return result.scalars().all()

@router.post("/trigger")
async def trigger_spawning(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Manually trigger spawning of due recurring expenses.
    """
    count = await recurring_service.spawn_due_expenses(db)
    return {"status": "success", "spawned_count": count}
