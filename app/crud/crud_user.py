from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        password_hash=hashed_password,
        is_active=user.is_active,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate(db: AsyncSession, email: str, password: str) -> Optional[User]:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

async def search_users(db: AsyncSession, query: str, limit: int = 20) -> list[User]:
    result = await db.execute(
        select(User)
        .filter(
            (User.username.ilike(f"%{query}%")) | 
            (User.email.ilike(f"%{query}%"))
        )
        .limit(limit)
    )
    return result.scalars().all()
