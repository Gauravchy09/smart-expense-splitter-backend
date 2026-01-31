from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from contextlib import asynccontextmanager
from app.db.session import engine
from app.db.base_class import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # Manual migration for category column if it doesn't exist
        from sqlalchemy import text
        await conn.execute(text("""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                             WHERE table_name='expense' AND column_name='category') THEN 
                    ALTER TABLE expense ADD COLUMN category VARCHAR DEFAULT 'Others' NOT NULL;
                END IF; 
                
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                             WHERE table_name='group' AND column_name='base_currency') THEN 
                    ALTER TABLE "group" ADD COLUMN base_currency VARCHAR DEFAULT 'USD' NOT NULL;
                END IF;

                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                             WHERE table_name='settlement' AND column_name='currency') THEN 
                    ALTER TABLE settlement ADD COLUMN currency VARCHAR DEFAULT 'USD' NOT NULL;
                END IF;
            END $$;
        """))
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/")
async def root():
    return {"message": "Welcome to Smart Expense Splitter API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)
