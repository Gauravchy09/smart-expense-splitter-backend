from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.group import Group, GroupMember
from app.models.user import User
from app.schemas.group import GroupCreate

async def create_group(db: AsyncSession, group: GroupCreate, owner_id: int) -> Group:
    db_group = Group(
        name=group.name,
        description=group.description,
        base_currency=group.base_currency,
        created_by=owner_id
    )
    db.add(db_group)
    await db.commit()
    await db.refresh(db_group)

    # Add owner as a member automatically
    db_member = GroupMember(group_id=db_group.id, user_id=owner_id)
    db.add(db_member)
    await db.commit()
    
    # Re-fetch with members loaded to satisfy response schema
    result = await db.execute(
        select(Group)
        .options(selectinload(Group.members))
        .where(Group.id == db_group.id)
    )
    return result.scalars().first()

async def get_multi_by_owner(db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 100) -> List[Group]:
    # This gets groups the user belongs to.
    print(f"FETCHING GROUPS FOR USER ID: {owner_id}")
    result = await db.execute(
        select(Group)
        .join(GroupMember)
        .filter(GroupMember.user_id == owner_id)
        .options(selectinload(Group.members).selectinload(GroupMember.user))
        .offset(skip)
        .limit(limit)
    )
    groups = result.scalars().unique().all()
    print(f"FOUND {len(groups)} GROUPS")
    return groups

async def get(db: AsyncSession, id: int) -> Optional[Group]:
    result = await db.execute(
        select(Group)
        .options(selectinload(Group.members).selectinload(GroupMember.user))
        .filter(Group.id == id)
    )
    return result.scalars().first()

async def add_member(db: AsyncSession, group_id: int, user_id: int) -> Optional[GroupMember]:
    # Check if already a member
    result = await db.execute(
        select(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        )
    )
    if result.scalars().first():
        return None
        
    db_member = GroupMember(group_id=group_id, user_id=user_id)
    db.add(db_member)
    await db.commit()
    await db.refresh(db_member)
    return db_member
