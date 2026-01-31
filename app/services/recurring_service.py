from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.recurring_expense import RecurringExpense
from app.models.expense import Expense, ExpenseSplit

async def spawn_due_expenses(db: AsyncSession):
    now = datetime.utcnow()
    # 1. Fetch due recurring expenses
    result = await db.execute(
        select(RecurringExpense).filter(
            RecurringExpense.status == "active",
            RecurringExpense.next_spawn_date <= now
        )
    )
    recurring_expenses = result.scalars().all()
    
    spawned_count = 0
    for re in recurring_expenses:
        # 2. Create the actual Expense
        new_expense = Expense(
            group_id=re.group_id,
            payer_id=re.payer_id,
            description=f"[Recurring] {re.description}",
            amount=re.amount,
            currency=re.currency,
            category=re.category,
            date=now
        )
        db.add(new_expense)
        await db.flush() # Get ID
        
        # 3. Create Splits
        for s in re.splits:
            split = ExpenseSplit(
                expense_id=new_expense.id,
                user_id=s['user_id'],
                amount_owed=s['amount_owed']
            )
            db.add(split)
            
        # 4. Update RecurringExpense for next time
        re.last_spawned_at = now
        if re.frequency == "daily":
            re.next_spawn_date = now + timedelta(days=1)
        elif re.frequency == "weekly":
            re.next_spawn_date = now + timedelta(weeks=1)
        elif re.frequency == "monthly":
            # Rough monthly jump
            re.next_spawn_date = now + timedelta(days=30)
        elif re.frequency == "yearly":
            re.next_spawn_date = now + timedelta(days=365)
            
        spawned_count += 1
        
    await db.commit()
    return spawned_count
