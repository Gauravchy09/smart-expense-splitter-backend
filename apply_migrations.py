import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def migrate():
    print(f"Starting migration to {settings.DATABASE_URL}...")
    engine = create_async_engine(settings.DATABASE_URL)
    print("Engine created.")
    async with engine.begin() as conn:
        print("Connection opened.")
        # 1. Add columns to group table
        try:
            await conn.execute(text("ALTER TABLE \"group\" ADD COLUMN IF NOT EXISTS base_currency VARCHAR DEFAULT 'USD' NOT NULL"))
            print("Added base_currency to group table")
        except Exception as e:
            print(f"Error adding base_currency to group: {e}")

        # 2. Add columns to settlement table
        try:
            await conn.execute(text("ALTER TABLE settlement ADD COLUMN IF NOT EXISTS currency VARCHAR DEFAULT 'USD' NOT NULL"))
            print("Added currency to settlement table")
        except Exception as e:
            print(f"Error adding currency to settlement: {e}")

        # 3. Create missing tables (recurring_expense, notification)
        # Import models to ensure they are registered with Base
        from app.db.base_class import Base
        from app.models.recurring_expense import RecurringExpense
        from app.models.notification import Notification
        
        # Base.metadata.create_all is synchronous, so we use run_sync
        await conn.run_sync(Base.metadata.create_all)
        print("Created all missing tables")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
