from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas import notification as schemas
from app.services import notification_service

router = APIRouter()

@router.get("/", response_model=List[schemas.Notification])
async def get_my_notifications(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get all unread notifications for the current user.
    """
    return await notification_service.get_unread_notifications(db, current_user.id)

@router.put("/{notification_id}/read", response_model=schemas.Notification)
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Mark a notification as read.
    """
    return await notification_service.mark_as_read(db, notification_id)
