from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.settlement import Settlement
from app.schemas.settlement import SettlementCreate

async def create_settlement(db: AsyncSession, settlement: SettlementCreate) -> Settlement:
    db_settlement = Settlement(
        group_id=settlement.group_id,
        payer_id=settlement.payer_id,
        payee_id=settlement.payee_id,
        amount=settlement.amount,
        currency=settlement.currency,
        status="completed" # Simplified: auto-complete for now
    )
    db.add(db_settlement)
    await db.commit()
    
    # Reload with relationships to satisfy response schema
    result = await db.execute(
        select(Settlement)
        .where(Settlement.id == db_settlement.id)
        .options(selectinload(Settlement.payer), selectinload(Settlement.payee))
    )
    return result.scalar_one()

async def get_settlements_by_group(db: AsyncSession, group_id: int) -> list[Settlement]:
    result = await db.execute(
        select(Settlement)
        .where(Settlement.group_id == group_id)
        .options(selectinload(Settlement.payer), selectinload(Settlement.payee))
        .order_by(Settlement.id.desc())
    )
    return result.scalars().all()
