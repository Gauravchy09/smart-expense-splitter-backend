from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.crud import crud_group
from app.models.user import User
from app.schemas.group import GroupCreate, Group as GroupSchema
from app.services import settlement_service, notification_service

router = APIRouter()

@router.post("/", response_model=GroupSchema)
async def create_group(
    *,
    db: AsyncSession = Depends(deps.get_db),
    group_in: GroupCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new group.
    """
    group = await crud_group.create_group(db=db, group=group_in, owner_id=current_user.id)
    return group

@router.get("/summary")
async def get_global_summary(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get global summary of what the user owes and is owed across all groups.
    """
    groups = await crud_group.get_multi_by_owner(db, owner_id=current_user.id)
    total_owed = 0.0 # Positive balances (others owe me)
    total_owe = 0.0  # Negative balances (I owe others)
    
    for group in groups:
        balances = await settlement_service.calculate_net_balances(db, group_id=group.id)
        user_balance = balances.get(current_user.id, 0.0)
        if user_balance > 0:
            total_owed += user_balance
        elif user_balance < 0:
            total_owe += abs(user_balance)
            
    return {
        "total_owed": round(total_owed, 2),
        "total_owe": round(total_owe, 2),
        "net_balance": round(total_owed - total_owe, 2),
        "group_count": len(groups)
    }

@router.get("/", response_model=List[GroupSchema])
async def read_groups(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve groups user belongs to.
    """
    groups = await crud_group.get_multi_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    return groups

@router.get("/{group_id}", response_model=GroupSchema)
async def read_group(
    group_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get group by ID.
    """
    group = await crud_group.get(db=db, id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    # In a real app, check if user is member of group
    return group
@router.post("/{group_id}/members/{user_id}", response_model=GroupSchema)
async def add_group_member(
    group_id: int,
    user_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Add a user to a group.
    """
    group = await crud_group.get(db=db, id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
        
    # Check if current user has permission (is owner or already a member)
    is_member = any(m.user_id == current_user.id for m in group.members)
    if group.created_by != current_user.id and not is_member:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    member = await crud_group.add_member(db=db, group_id=group_id, user_id=user_id)
    if not member:
        # Already a member, just return group
        return group
    
    # Notify the user they were added
    await notification_service.create_notification(
        db, 
        user_id=user_id, 
        message=f"You have been added to the group '{group.name}'", 
        type="group_invite"
    )
        
    # Re-fetch group to get updated members
    updated_group = await crud_group.get(db=db, id=group_id)
    return updated_group

@router.get("/{group_id}/balances")
async def get_group_balances(
    group_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get net balances and simplified transactions for a group.
    """
    balances = await settlement_service.calculate_net_balances(db, group_id=group_id)
    transactions = settlement_service.simplify_debts(balances)
    
    # Enrich balances with usernames
    enriched_balances = []
    for uid, bal in balances.items():
        # This is a bit inefficient, but fine for small groups. 
        # In a real app we'd fetch all users at once.
        user_result = await db.execute(select(User).filter(User.id == uid))
        user = user_result.scalars().first()
        enriched_balances.append({
            "user_id": uid,
            "username": user.username if user else f"User {uid}",
            "balance": round(bal, 2)
        })

    # Enrich transactions with usernames
    enriched_transactions = []
    for tx in transactions:
        from_user_res = await db.execute(select(User).filter(User.id == tx['from_id']))
        from_user = from_user_res.scalars().first()
        to_user_res = await db.execute(select(User).filter(User.id == tx['to_id']))
        to_user = to_user_res.scalars().first()
        
        enriched_transactions.append({
            "from_id": tx['from_id'],
            "from_name": from_user.username if from_user else f"User {tx['from_id']}",
            "to_id": tx['to_id'],
            "to_name": to_user.username if to_user else f"User {tx['to_id']}",
            "amount": tx['amount']
        })

    return {
        "balances": enriched_balances,
        "suggested_transactions": enriched_transactions
    }
from sqlalchemy import select
