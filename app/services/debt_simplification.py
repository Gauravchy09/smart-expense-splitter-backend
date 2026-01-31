from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.expense import Expense, ExpenseSplit
from app.models.settlement import Settlement

async def calculate_debts(db: AsyncSession, group_id: int) -> List[Dict]:
    # 1. Get all expenses for the group
    expenses_query = await db.execute(
        select(Expense).filter(Expense.group_id == group_id)
    )
    expenses = expenses_query.scalars().all()
    
    # 2. Calculate net balance for each user
    # balances[user_id] = net_amount (positive = receives, negative = owes)
    balances = {}

    for expense in expenses:
        # Payer paid full amount
        balances[expense.payer_id] = balances.get(expense.payer_id, 0) + expense.amount
        
        # Load splits (assuming loaded or verify fetch)
        # Note: In real app, ensure eagerly loaded or fetch separately
        splits_query = await db.execute(select(ExpenseSplit).filter(ExpenseSplit.expense_id == expense.id))
        splits = splits_query.scalars().all()

        for split in splits:
            balances[split.user_id] = balances.get(split.user_id, 0) - split.amount_owed

    # 3. Simplify Debts (Greedy Algorithm)
    debtors = []
    creditors = []

    for user_id, amount in balances.items():
        if amount < -0.01: # Owes money
            debtors.append({'id': user_id, 'amount': amount})
        elif amount > 0.01: # Is owed money
            creditors.append({'id': user_id, 'amount': amount})

    # Sort by magnitude (heuristic for fewer transactions)
    debtors.sort(key=lambda x: x['amount']) # Ascending (most negative first)
    creditors.sort(key=lambda x: x['amount'], reverse=True) # Descending (most positive first)

    settlements = []
    
    i = 0 # debtor index
    j = 0 # creditor index

    while i < len(debtors) and j < len(creditors):
        debtor = debtors[i]
        creditor = creditors[j]

        # Amount to settle
        amount = min(abs(debtor['amount']), creditor['amount'])
        
        settlements.append({
            "payer_id": debtor['id'],
            "payee_id": creditor['id'],
            "amount": round(amount, 2)
        })

        # Update remaining
        debtor['amount'] += amount
        creditor['amount'] -= amount

        if abs(debtor['amount']) < 0.01:
            i += 1
        if creditor['amount'] < 0.01:
            j += 1
            
    return settlements
