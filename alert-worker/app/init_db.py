import asyncio
from app.db import engine
from app.models import Base, Video  # importe tous tes modèles pour qu'ils soient enregistrés

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
