from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.crud import crud_expense
from app.models.user import User
from app.schemas.expense import ExpenseCreate, Expense as ExpenseSchema
from app.services import notification_service
from app.crud import crud_group

router = APIRouter()

@router.post("/", response_model=ExpenseSchema)
async def create_expense(
    *,
    db: AsyncSession = Depends(deps.get_db),
    expense_in: ExpenseCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new expense.
    """
    expense = await crud_expense.create_expense(db=db, expense=expense_in, payer_id=current_user.id)
    
    # Notify other group members
    group = await crud_group.get(db, id=expense_in.group_id)
    if group:
        for member in group.members:
            if member.user_id != current_user.id:
                await notification_service.create_notification(
                    db,
                    user_id=member.user_id,
                    message=f"{current_user.username} added a new expense '{expense.description}' in '{group.name}'",
                    type="expense"
                )
    
    return expense

@router.get("/group/{group_id}", response_model=List[ExpenseSchema])
async def read_expenses(
    group_id: int,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve expenses for a group.
    """
    expenses = await crud_expense.get_multi_by_group(db, group_id=group_id, skip=skip, limit=limit)
    return expenses

@router.put("/{expense_id}", response_model=ExpenseSchema)
async def update_expense(
    expense_id: int,
    expense_in: ExpenseCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update an expense.
    """
    expense = await crud_expense.update_expense(db, expense_id=expense_id, expense_in=expense_in)
    if not expense:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete an expense.
    """
    success = await crud_expense.delete_expense(db, expense_id=expense_id)
    if not success:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}
