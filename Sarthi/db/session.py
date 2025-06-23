# db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from dotenv import load_dotenv
import os
from typing import AsyncGenerator

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,  # ✅ Key fix for pgbouncer
        "server_settings": {
            "application_name": "reflection_platform",
        }
    }
)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()