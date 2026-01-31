from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core import security
from app.crud import crud_user
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema

router = APIRouter()

@router.post("/", response_model=UserSchema)
async def create_user_signup(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = await crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = await crud_user.create_user(db=db, user=user_in)
    return user

@router.get("/me", response_model=UserSchema)
async def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.get("/search", response_model=List[UserSchema])
async def search_users(
    query: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Search for users.
    """
    users = await crud_user.search_users(db, query=query)
    return users
