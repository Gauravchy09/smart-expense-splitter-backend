from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.notification import Notification

async def create_notification(db: AsyncSession, user_id: int, message: str, type: str):
    notification = Notification(
        user_id=user_id,
        message=message,
        type=type
    )
    db.add(notification)
    await db.commit()
    return notification

async def get_unread_notifications(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read == False)
        .order_by(Notification.created_at.desc())
    )
    return result.scalars().all()

async def mark_as_read(db: AsyncSession, notification_id: int):
    result = await db.execute(select(Notification).filter(Notification.id == notification_id))
    notification = result.scalars().first()
    if notification:
        notification.is_read = True
        await db.commit()
    return notification
