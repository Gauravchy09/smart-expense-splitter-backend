import asyncio
import os
import sys

# Add the current directory to sys.path so 'app' can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal, engine
from app.models.user import User
from app.models.group import Group, GroupMember

async def check():
    print("Connecting to database...")
    try:
        async with AsyncSessionLocal() as db:
            # Find Yug
            res = await db.execute(select(User).filter(User.username.ilike("%yug%")))
            yug = res.scalars().first()
            if not yug:
                print("User 'yug' not found!")
                return
            
            print(f"Found Yug: ID={yug.id}, Username={yug.username}")
            
            # Find memberships
            res = await db.execute(select(GroupMember).filter(GroupMember.user_id == yug.id))
            memberships = res.scalars().all()
            print(f"Yug belongs to {len(memberships)} groups.")
            for m in memberships:
                # Get group name
                gres = await db.execute(select(Group).filter(Group.id == m.group_id))
                group = gres.scalars().first()
                print(f" - Group ID: {m.group_id}, Name: {group.name if group else 'Unknown'}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check())
