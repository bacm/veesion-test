import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.models import Video


# --- DB CONFIG ---
DB_USER = os.getenv("POSTGRES_USER", "veesion")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "secret")
DB_NAME = os.getenv("POSTGRES_DB", "veesion")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def save_video(uid: str, video: str, width: int, height: int):
    async with AsyncSessionLocal() as session:
        video_entry = Video(uid=uid, video=video, width=width, height=height)
        session.add(video_entry)
        await session.commit()
