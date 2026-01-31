import asyncio
import asyncpg
import sys
import os
sys.path.append(os.getcwd())
from app.core.config import settings

async def migrate():
    # Parse asyncpg URL (remove sqlalchemy prefix if present)
    url = settings.DATABASE_URL
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://")
    
    conn = await asyncpg.connect(url)
    try:
        # Check if category column exists
        exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name='expense' AND column_name='category'
            );
        """)
        
        if not exists:
            print("Adding 'category' column to 'expense' table...")
            await conn.execute("ALTER TABLE expense ADD COLUMN category VARCHAR DEFAULT 'Others' NOT NULL;")
            print("Successfully added 'category' column.")
        else:
            print("'category' column already exists.")
            
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(migrate())
