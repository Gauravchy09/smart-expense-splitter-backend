from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.expense import Expense, ExpenseSplit
from app.schemas.expense import ExpenseCreate

async def create_expense(db: AsyncSession, expense: ExpenseCreate, payer_id: int) -> Expense:
    db_expense = Expense(
        group_id=expense.group_id,
        payer_id=payer_id,
        description=expense.description,
        amount=expense.amount,
        currency=expense.currency,
        category=expense.category,
        date=expense.date,
        receipt_image_url=expense.receipt_image_url if hasattr(expense, 'receipt_image_url') else None # Handle optional field
    )
    db.add(db_expense)
    await db.commit()
    await db.refresh(db_expense)

    for split in expense.splits:
        db_split = ExpenseSplit(
            expense_id=db_expense.id,
            user_id=split.user_id,
            amount_owed=split.amount_owed
        )
        db.add(db_split)
    
    await db.commit()
    return db_expense

from sqlalchemy.orm import selectinload

async def get_multi_by_group(db: AsyncSession, group_id: int, skip: int = 0, limit: int = 100) -> List[Expense]:
    result = await db.execute(
        select(Expense)
        .filter(Expense.group_id == group_id)
        .options(selectinload(Expense.splits))
        .order_by(Expense.date.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def update_expense(db: AsyncSession, expense_id: int, expense_in: ExpenseCreate) -> Expense:
    result = await db.execute(
        select(Expense)
        .filter(Expense.id == expense_id)
        .options(selectinload(Expense.splits))
    )
    db_expense = result.scalars().first()
    if not db_expense:
        return None
    
    db_expense.description = expense_in.description
    db_expense.amount = expense_in.amount
    db_expense.category = expense_in.category
    db_expense.date = expense_in.date
    
    # Update splits - using delete-orphan cascade
    db_expense.splits = [
        ExpenseSplit(user_id=s.user_id, amount_owed=s.amount_owed)
        for s in expense_in.splits
    ]
    
    await db.commit()
    await db.refresh(db_expense)
    return db_expense

async def delete_expense(db: AsyncSession, expense_id: int) -> bool:
    result = await db.execute(select(Expense).filter(Expense.id == expense_id))
    db_expense = result.scalars().first()
    if not db_expense:
        return False
    
    # Splits are automatically deleted due to cascade if using SQLAlchemy relationships correctly,
    # but here we'll be explicit if needed or trust the cascading model.
    # Looking at models, if not specified, we should delete them.
    await db.delete(db_expense)
    await db.commit()
    return True
