from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.expense import Expense, ExpenseSplit
from app.models.group import GroupMember, Group
from app.models.settlement import Settlement

def get_exchange_rate(from_curr: str, to_curr: str) -> float:
    """
    Mock exchange rate service. In a real app, this would call an external API.
    """
    from_curr = from_curr.upper()
    to_curr = to_curr.upper()
    if from_curr == to_curr:
        return 1.0
    
    # Fixed mock rates for common currencies
    rates = {
        ("USD", "EUR"): 0.92,
        ("EUR", "USD"): 1.09,
        ("USD", "GBP"): 0.79,
        ("GBP", "USD"): 1.27,
        ("USD", "INR"): 83.0,
        ("INR", "USD"): 0.012,
        ("EUR", "GBP"): 0.86,
        ("GBP", "EUR"): 1.16,
    }
    return rates.get((from_curr, to_curr), 1.0) # Default to 1.0 if not found

async def calculate_net_balances(db: AsyncSession, group_id: int) -> Dict[int, float]:
    """
    Calculate the net balance for each member in the group.
    Net Balance = Total Paid - Total Owed
    All values are converted to the group's base_currency.
    """
    # 1. Get Group and its base_currency
    group_res = await db.execute(select(Group).filter(Group.id == group_id))
    group = group_res.scalars().first()
    if not group:
        return {}
    base_currency = getattr(group, 'base_currency', 'USD')

    # 2. Get all members
    member_result = await db.execute(select(GroupMember.user_id).filter(GroupMember.group_id == group_id))
    members = member_result.scalars().all()
    balances = {uid: 0.0 for uid in members}

    # 3. Total Paid by each user (with conversion)
    paid_result = await db.execute(
        select(Expense.payer_id, Expense.amount, Expense.currency)
        .filter(Expense.group_id == group_id)
    )
    for payer_id, amount, currency in paid_result.all():
        if payer_id in balances:
            rate = get_exchange_rate(currency, base_currency)
            balances[payer_id] += float(amount) * rate

    # 4. Total Owed by each user (with conversion)
    owed_result = await db.execute(
        select(ExpenseSplit.user_id, ExpenseSplit.amount_owed, Expense.currency)
        .join(Expense, Expense.id == ExpenseSplit.expense_id)
        .filter(Expense.group_id == group_id)
    )
    for user_id, amount_owed, currency in owed_result.all():
        if user_id in balances:
            rate = get_exchange_rate(currency, base_currency)
            balances[user_id] -= float(amount_owed) * rate
    
    # 5. Total Paid in Settlements (with conversion)
    settlement_paid = await db.execute(
        select(Settlement.payer_id, Settlement.amount, Settlement.currency)
        .filter(Settlement.group_id == group_id)
    )
    for payer_id, amount, currency in settlement_paid.all():
        if payer_id in balances:
            rate = get_exchange_rate(currency, base_currency)
            balances[payer_id] += float(amount) * rate

    # 6. Total Received in Settlements (with conversion)
    settlement_received = await db.execute(
        select(Settlement.payee_id, Settlement.amount, Settlement.currency)
        .filter(Settlement.group_id == group_id)
    )
    for payee_id, amount, currency in settlement_received.all():
        if payee_id in balances:
            rate = get_exchange_rate(currency, base_currency)
            balances[payee_id] -= float(amount) * rate
    
    return balances

def simplify_debts(balances: Dict[int, float]) -> List[Dict[str, Any]]:
    """
    Greedy algorithm to simplify debts.
    Returns a list of suggested transactions: { 'from': uid, 'to': uid, 'amount': value }
    """
    debtors = [] # Negative balance
    creditors = [] # Positive balance

    for uid, bal in balances.items():
        if bal < -0.01: # Use a small epsilon for float precision
            debtors.append({'uid': uid, 'bal': abs(bal)})
        elif bal > 0.01:
            creditors.append({'uid': uid, 'bal': bal})

    debtors.sort(key=lambda x: x['bal'], reverse=True)
    creditors.sort(key=lambda x: x['bal'], reverse=True)

    transactions = []
    i = 0
    j = 0

    while i < len(debtors) and j < len(creditors):
        amount = min(debtors[i]['bal'], creditors[j]['bal'])
        transactions.append({
            'from_id': debtors[i]['uid'],
            'to_id': creditors[j]['uid'],
            'amount': round(amount, 2)
        })

        debtors[i]['bal'] -= amount
        creditors[j]['bal'] -= amount

        if debtors[i]['bal'] < 0.01:
            i += 1
        if creditors[j]['bal'] < 0.01:
            j += 1

    return transactions
