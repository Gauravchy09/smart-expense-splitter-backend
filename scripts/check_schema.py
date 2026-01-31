import asyncio
import asyncpg
import sys
import os
sys.path.append(os.getcwd())
from app.core.config import settings

async def check_schema():
    url = settings.DATABASE_URL
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://")
    
    try:
        conn = await asyncpg.connect(url)
        print(f"Connected to {url}")
        columns = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='expense'
            ORDER BY ordinal_position;
        """)
        print("Columns in 'expense' table:")
        for col in columns:
            print(f" - {col['column_name']}")
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_schema())
